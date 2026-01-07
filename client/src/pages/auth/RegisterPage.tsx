import { useCallback, useEffect, useMemo, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";

import FormInput from "../../components/FormInput";
import PasswordMeter from "../../components/PasswordMeter";
import Recaptcha from "../../components/Recaptcha";
import RoleCard from "../../components/RoleCard";
import SkillMultiSelect from "../../components/SkillMultiSelect";
import {
  registerStep1,
  registerStep2,
  trackAnalyticsEvent,
  type RegisterStep1Payload,
  type RegisterStep2Payload,
  type RegisterStep2Response,
  type UserRole,
} from "../../lib/authApi";
import { useAuth } from "../../features/auth/AuthContext";

const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$/;
const PASSWORD_ERROR =
  "Password must be at least 12 characters and include uppercase, lowercase, digit, and special character.";

const step1Schema = z
  .object({
    first_name: z.string().min(1, "First name is required").max(50),
    last_name: z.string().min(1, "Last name is required").max(50),
    email: z.string().email("Enter a valid email address"),
    password: z.string().regex(PASSWORD_REGEX, PASSWORD_ERROR),
    confirm_password: z.string(),
    role: z.enum(["Customer", "Developer"]),
    recaptcha_token: z.string().min(1, "Complete the reCAPTCHA"),
  })
  .refine((data) => data.password === data.confirm_password, {
    path: ["confirm_password"],
    message: "Passwords do not match.",
  });

const customerStep2Schema = z.object({
  role: z.literal("Customer"),
  company_name: z.string().min(1, "Company name is required").max(100),
  industry: z.string().min(1, "Select an industry"),
  company_size: z.string().min(1, "Select a company size"),
  use_cases: z.array(z.string()).min(1, "Pick at least one use case"),
  budget_range: z.string().min(1, "Select a budget range"),
});

const developerStep2Schema = z.object({
  role: z.literal("Developer"),
  company_name: z.string().min(1, "Company name is required").max(100),
  skills: z.array(z.string()).min(1, "Add at least one skill"),
  experience_level: z.string().min(1, "Select an experience level"),
  portfolio_link: z
    .string()
    .optional()
    .transform((value) => value?.trim() ?? "")
    .refine((value) => !value || /^https?:\/\//.test(value), "Enter a valid URL"),
  availability: z.string().min(1, "Select your availability"),
});

const step2Schema = z.discriminatedUnion("role", [customerStep2Schema, developerStep2Schema]);

type Step1Values = z.infer<typeof step1Schema>;
type Step2Values = z.infer<typeof step2Schema>;

const CUSTOMER_USE_CASES = [
  "Prototyping new workflows",
  "Improving internal tools",
  "Customer support automation",
  "Data analysis",
];

const INDUSTRY_OPTIONS = ["Technology", "Finance", "Retail", "Healthcare", "Other"];
const COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-1000", "1000+"];
const BUDGET_RANGES = ["<$1k", "$1k-$5k", "$5k-$20k", ">$20k"];
const EXPERIENCE_LEVELS = ["Junior", "Mid-level", "Senior", "Principal"];
const AVAILABILITY_OPTIONS = ["Less than 10 hours/week", "10-20 hours/week", "Full-time"];

const Register = () => {
  const [step, setStep] = useState<1 | 2>(1);
  const [tempToken, setTempToken] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const navigate = useNavigate();
  const { setAuthFromTokens } = useAuth();

  const sendAnalytics = useCallback(async (payload: { event_type: string; step?: string; role?: UserRole | null; details?: Record<string, unknown> }) => {
    try {
      await trackAnalyticsEvent({
        event_type: payload.event_type,
        step: payload.step ?? null,
        role: payload.role ?? null,
        details: payload.details ?? {},
      });
    } catch (err) {
      console.warn("Analytics event failed", err);
    }
  }, []);

  const recaptchaSiteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY as string | undefined;

  const step1Form = useForm<Step1Values>({
    resolver: zodResolver(step1Schema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      password: "",
      confirm_password: "",
      role: "Customer",
      recaptcha_token: recaptchaSiteKey ? "" : "dev-bypass-token",
    },
  });

  useEffect(() => {
    step1Form.register("recaptcha_token");
    if (!recaptchaSiteKey) {
      step1Form.setValue("recaptcha_token", "dev-bypass-token", {
        shouldValidate: false,
        shouldDirty: false,
      });
    }
  }, [recaptchaSiteKey, step1Form]);

  const step1Role = step1Form.watch("role");

  const step2Form = useForm<Step2Values>({
    resolver: zodResolver(step2Schema),
    defaultValues: {
      role: "Customer",
      company_name: "",
      industry: "",
      company_size: "",
      use_cases: [],
      budget_range: "",
    } as Step2Values,
  });

  const step2Role = step2Form.watch("role");

  // Helper function to safely access error messages for discriminated union fields
  const getErrorMessage = (fieldName: string): string | undefined => {
    const errors = step2Form.formState.errors;
    return (errors as any)[fieldName]?.message;
  };

  useEffect(() => {
    sendAnalytics({ event_type: "step_view", step: "step1", role: step1Role });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (step === 2) {
      sendAnalytics({ event_type: "step_view", step: "step2", role: step2Role });
    }
  }, [sendAnalytics, step, step2Role]);

  const step1Mutation = useMutation({
    mutationFn: (payload: RegisterStep1Payload) => registerStep1(payload),
  });

  const step2Mutation = useMutation({
    mutationFn: ({ payload, token }: { payload: RegisterStep2Payload; token: string }) =>
      registerStep2(payload, token),
  });

  const handleRecaptchaVerify = useCallback(
    (token: string | null) =>
      step1Form.setValue("recaptcha_token", token ?? "", { shouldValidate: true }),
    [step1Form],
  );

  const handleRoleSelect = (role: UserRole) => {
    step1Form.setValue("role", role, { shouldValidate: true });
    sendAnalytics({ event_type: "role_selected", step: "step1", role });
  };

  const onStep1Submit = async (values: Step1Values) => {
    setApiError(null);
    try {
      const response = await step1Mutation.mutateAsync(values);
      setTempToken(response.temp_token);
      setStep(2);
      const role = values.role;
      if (role === "Customer") {
        step2Form.reset({
          role: "Customer",
          company_name: "",
          industry: "",
          company_size: "",
          use_cases: [],
          budget_range: "",
        } as Step2Values);
      } else {
        step2Form.reset({
          role: "Developer",
          company_name: "",
          skills: [],
          experience_level: "",
          portfolio_link: "",
          availability: "",
        } as Step2Values);
      }
      await sendAnalytics({ event_type: "step_submit", step: "step1", role });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to start registration";
      setApiError(message);
      await sendAnalytics({ event_type: "error", step: "step1", role: values.role, details: { message } });
    }
  };

  const onStep2Submit = async (values: Step2Values) => {
    if (!tempToken) {
      setApiError("Registration session expired. Please restart step 1.");
      setStep(1);
      return;
    }

    setApiError(null);
    const payload: RegisterStep2Payload = {
      company_name: values.company_name,
      profile: values.role === "Customer"
        ? {
            industry: values.industry,
            company_size: values.company_size,
            use_cases: values.use_cases,
            budget_range: values.budget_range,
          }
        : {
            skills: values.skills,
            experience_level: values.experience_level,
            portfolio_link: values.portfolio_link,
            availability: values.availability,
          },
    };

    try {
      const result: RegisterStep2Response = await step2Mutation.mutateAsync({ payload, token: tempToken });
      setAuthFromTokens(
        result.user.email,
        {
          access_token: result.access_token,
          refresh_token: result.refresh_token,
          expires_at: result.expires_at,
          email_verified: result.user.email_verified,
        },
        result.user.email_verified ?? false,
      );
      await sendAnalytics({ event_type: "step_submit", step: "step2", role: result.user.role });
      await sendAnalytics({ event_type: "complete", role: result.user.role });

      if (result.user.role === "Customer") {
        navigate("/onboarding/customer", { replace: true });
      } else {
        navigate("/onboarding/developer", { replace: true });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to complete registration";
      setApiError(message);
      await sendAnalytics({ event_type: "error", step: "step2", role: values.role, details: { message } });
    }
  };

  const progress = useMemo(() => (step === 1 ? 50 : 100), [step]);

  return (
    <main className="register-page">
      <section className="register-card">
        <header className="register-card__header">
          <h1>Create your CapeControl account</h1>
          <p>Two quick steps to tailor the experience for customers and developers.</p>
          <div className="register-card__progress" aria-label={`Progress ${progress}%`}>
            <div className="register-card__progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <p className="register-card__step">Step {step} of 2</p>
        </header>

        {apiError && <div className="register-card__error">{apiError}</div>}

        {step === 1 ? (
          <form className="register-form" onSubmit={step1Form.handleSubmit(onStep1Submit)}>
            <div className="register-role-grid">
              <RoleCard
                role="Customer"
                title="Customer"
                description="Find developers and agents that accelerate your roadmap."
                selected={step1Role === "Customer"}
                onSelect={handleRoleSelect}
              />
              <RoleCard
                role="Developer"
                title="Developer"
                description="Showcase your skills, match with customers, and manage engagements."
                selected={step1Role === "Developer"}
                onSelect={handleRoleSelect}
              />
            </div>

            <div className="register-form__grid">
              <FormInput label="First name" error={step1Form.formState.errors.first_name?.message}>
                <input type="text" {...step1Form.register("first_name")}
                  placeholder="Ada" />
              </FormInput>
              <FormInput label="Last name" error={step1Form.formState.errors.last_name?.message}>
                <input type="text" {...step1Form.register("last_name")}
                  placeholder="Lovelace" />
              </FormInput>
            </div>

            <FormInput label="Work email" error={step1Form.formState.errors.email?.message}>
              <input type="email" {...step1Form.register("email")}
                placeholder="you@company.com" autoComplete="email" />
            </FormInput>

            <FormInput label="Password" error={step1Form.formState.errors.password?.message}>
              <div className="form-input__password">
                <input
                  type={showPassword ? "text" : "password"}
                  {...step1Form.register("password")}
                  placeholder="Create a strong password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="form-input__password-toggle"
                  onClick={() => setShowPassword((prev) => !prev)}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </FormInput>
            <PasswordMeter password={step1Form.watch("password")} />

            <FormInput label="Confirm password" error={step1Form.formState.errors.confirm_password?.message}>
              <div className="form-input__password">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  {...step1Form.register("confirm_password")}
                  placeholder="Re-enter password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="form-input__password-toggle"
                  onClick={() => setShowConfirmPassword((prev) => !prev)}
                >
                  {showConfirmPassword ? "Hide" : "Show"}
                </button>
              </div>
            </FormInput>

            <input type="hidden" {...step1Form.register("role")}
              value={step1Role} />

            {recaptchaSiteKey ? (
              <Recaptcha
                onVerify={handleRecaptchaVerify}
                error={step1Form.formState.errors.recaptcha_token?.message}
              />
            ) : (
              <div className="recaptcha-placeholder">
                <p className="recaptcha-placeholder__info">
                  reCAPTCHA is not configured. Set <code>VITE_RECAPTCHA_SITE_KEY</code> when you are ready to
                  enforce verification. A temporary bypass token has been supplied for local testing.
                </p>
              </div>
            )}

            <button
              className="register-form__submit"
              type="submit"
              disabled={step1Mutation.isPending}
            >
              {step1Mutation.isPending ? "Processing…" : "Continue"}
            </button>
          </form>
        ) : (
          <form className="register-form" onSubmit={step2Form.handleSubmit(onStep2Submit)}>
            <input type="hidden" {...step2Form.register("role")} value={step2Role} />

            <FormInput label="Company name" error={step2Form.formState.errors.company_name?.message}>
              <input type="text" {...step2Form.register("company_name")}
                placeholder="Your company" />
            </FormInput>

            {step2Role === "Customer" ? (
              <>
                <FormInput label="Industry" error={getErrorMessage("industry")}>
                  <select {...step2Form.register("industry")}>
                    <option value="">Select industry</option>
                    {INDUSTRY_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </FormInput>

                <FormInput label="Company size" error={getErrorMessage("company_size")}>
                  <select {...step2Form.register("company_size")}>
                    <option value="">Select size</option>
                    {COMPANY_SIZES.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </FormInput>

                <Controller
                  control={step2Form.control}
                  name="use_cases"
                  render={({ field }) => (
                    <FormInput label="Primary use cases" error={getErrorMessage("use_cases")}>
                      <div className="checkbox-grid">
                        {CUSTOMER_USE_CASES.map((option) => {
                          const checked = field.value?.includes(option) ?? false;
                          return (
                            <label key={option}>
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={(event) => {
                                  if (event.target.checked) {
                                    field.onChange([...(field.value ?? []), option]);
                                  } else {
                                    field.onChange((field.value ?? []).filter((item) => item !== option));
                                  }
                                }}
                              />
                              {option}
                            </label>
                          );
                        })}
                      </div>
                    </FormInput>
                  )}
                />

                <FormInput label="Budget range" error={getErrorMessage("budget_range")}>
                  <select {...step2Form.register("budget_range")}>
                    <option value="">Select budget</option>
                    {BUDGET_RANGES.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </FormInput>
              </>
            ) : (
              <>
                <Controller
                  control={step2Form.control}
                  name="skills"
                  render={({ field }) => (
                    <FormInput label="Key skills" error={getErrorMessage("skills")}>
                      <SkillMultiSelect value={field.value ?? []} onChange={field.onChange} />
                    </FormInput>
                  )}
                />

                <FormInput label="Experience level" error={getErrorMessage("experience_level")}>
                  <select {...step2Form.register("experience_level")}>
                    <option value="">Select level</option>
                    {EXPERIENCE_LEVELS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </FormInput>

                <FormInput label="Portfolio link (optional)" error={getErrorMessage("portfolio_link")}>
                  <input type="url" {...step2Form.register("portfolio_link")}
                    placeholder="https://" />
                </FormInput>

                <FormInput label="Availability" error={getErrorMessage("availability")}>
                  <select {...step2Form.register("availability")}>
                    <option value="">Select availability</option>
                    {AVAILABILITY_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </FormInput>
              </>
            )}

            <button
              className="register-form__submit"
              type="submit"
              disabled={step2Mutation.isPending}
            >
              {step2Mutation.isPending ? "Finishing…" : "Create account"}
            </button>
          </form>
        )}
      </section>
    </main>
  );
};

export default Register;
