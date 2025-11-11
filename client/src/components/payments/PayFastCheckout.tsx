import { FormEvent, useEffect, useMemo } from "react";
import FormInput from "../FormInput";
import type { CheckoutDetailsStepProps } from "./CheckoutFlow";
import { VALIDATION_RULES } from "../../types/payments";
import { PaymentSecurityValidator } from "../../services/paymentsApi";
import { useSecureFormInput } from "../../hooks/usePayments";
import {
  usePaymentSecurity as useSecurityContext,
  SecurityEventList,
} from "./PaymentSecurityProvider";

type PayFastCheckoutProps = CheckoutDetailsStepProps;

const FIELD_COPY = {
  amount: `Between ZAR ${VALIDATION_RULES.AMOUNT.MIN.toFixed(2)} and ZAR ${VALIDATION_RULES.AMOUNT.MAX.toFixed(2)}`,
  itemName: `Min ${VALIDATION_RULES.ITEM_NAME.MIN_LENGTH} characters`,
  customerEmail: "We use this for PayFast receipts",
  customerFirstName: "Only alphabetic characters allowed",
  customerLastName: "Only alphabetic characters allowed",
};

function getFieldError(
  validation: CheckoutDetailsStepProps["validation"],
  field: keyof CheckoutDetailsStepProps["validation"],
  fallback: string,
) {
  const state = validation[field];
  if (!state || !state.touched) {
    return undefined;
  }
  if (!state.isValid) {
    return state.error ?? fallback;
  }
  return undefined;
}

const PayFastCheckout = ({
  formData,
  validation,
  formRefs,
  amountError,
  formattedAmount,
  validationResult,
  onUpdateFormData,
  onNext,
  onCancel,
  isValid,
}: PayFastCheckoutProps) => {
  const { isSecureContext, csrfToken, refreshCSRFToken, rateLimitInfo } = useSecurityContext();

  const {
    hasSecurityIssues: descriptionHasSecurityIssues,
    updateValue: updateDescriptionSecurity,
  } = useSecureFormInput(formData.itemDescription || "");

  useEffect(() => {
    updateDescriptionSecurity(formData.itemDescription || "");
  }, [formData.itemDescription, updateDescriptionSecurity]);

  const checkoutPreview = useMemo(
    () => ({
      amount: Number.parseFloat(formData.amount) || 0,
      itemName: formData.itemName,
      itemDescription: formData.itemDescription || undefined,
      customerEmail: formData.customerEmail,
      customerFirstName: formData.customerFirstName,
      customerLastName: formData.customerLastName,
      metadata: { source: "checkout" },
    }),
    [
      formData.amount,
      formData.itemName,
      formData.itemDescription,
      formData.customerEmail,
      formData.customerFirstName,
      formData.customerLastName,
    ],
  );

  const securityValidation = useMemo(
    () => PaymentSecurityValidator.validateCheckoutRequest(checkoutPreview),
    [checkoutPreview],
  );

  const combinedValidation = validationResult ?? securityValidation;

  const itemNameError = getFieldError(validation, "itemName", "Enter an item name.");
  const emailError = getFieldError(validation, "customerEmail", "Enter a valid email address.");
  const firstNameError = getFieldError(validation, "customerFirstName", "First name is required.");
  const lastNameError = getFieldError(validation, "customerLastName", "Last name is required.");
  const agreeToTermsError = getFieldError(validation, "agreeToTerms", "Please confirm authorization.");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isValid) {
      onNext();
    }
  };

  return (
    <section className="payfast-checkout-step">
      <header className="payfast-checkout-step__header">
        <div>
          <h2>Payment details</h2>
          <p>Securely prepare your PayFast checkout session.</p>
        </div>
        <div className="payfast-checkout-step__summary">
          <span>Total preview</span>
          <strong>{formattedAmount || "ZAR 0.00"}</strong>
        </div>
      </header>

      <div className="payfast-checkout-step__security">
        <div>
          <small>Secure context</small>
          <strong>{isSecureContext ? "Verified" : "Required"}</strong>
        </div>
        <div>
          <small>CSRF token</small>
          <span>
            {csrfToken ? "Active" : "Refreshing…"}{" "}
            <button type="button" className="link" onClick={refreshCSRFToken}>
              Refresh
            </button>
          </span>
        </div>
        <div>
          <small>Attempts</small>
          <span>
            {rateLimitInfo.attempts}/{rateLimitInfo.maxAttempts}
          </span>
        </div>
      </div>

      {(combinedValidation.errors?.length > 0 || combinedValidation.warnings?.length > 0) && (
        <div className="payfast-checkout-step__validation" aria-live="assertive">
          {combinedValidation.errors?.length > 0 && (
            <div className="alert alert-danger">
              <strong>Security validation</strong>
              <ul>
                {combinedValidation.errors.map((message: string) => (
                  <li key={message}>{message}</li>
                ))}
              </ul>
            </div>
          )}
          {combinedValidation.warnings?.length > 0 && (
            <div className="alert alert-warning" role="status">
              <strong>Warnings</strong>
              <ul>
                {combinedValidation.warnings.map((message: string) => (
                  <li key={message}>{message}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <form className="payfast-checkout-step__form" onSubmit={handleSubmit} noValidate>
        <FormInput label="Amount (ZAR)" description={FIELD_COPY.amount} error={amountError || undefined}>
          <input
            ref={formRefs.amount}
            type="number"
            inputMode="decimal"
            min={VALIDATION_RULES.AMOUNT.MIN}
            max={VALIDATION_RULES.AMOUNT.MAX}
            step="0.01"
            value={formData.amount}
            onChange={(event) => onUpdateFormData("amount", event.target.value)}
            required
          />
        </FormInput>

        <FormInput label="Item name" description={FIELD_COPY.itemName} error={itemNameError}>
          <input
            ref={formRefs.itemName}
            type="text"
            value={formData.itemName}
            onChange={(event) => onUpdateFormData("itemName", event.target.value)}
            maxLength={VALIDATION_RULES.ITEM_NAME.MAX_LENGTH}
            required
          />
        </FormInput>

        <FormInput
          label="Item description"
          description="Shown on the PayFast confirmation screen (optional)."
          error={descriptionHasSecurityIssues ? "Suspicious characters were removed for safety." : undefined}
        >
          <textarea
            value={formData.itemDescription}
            onChange={(event) => {
              updateDescriptionSecurity(event.target.value);
              onUpdateFormData("itemDescription", event.target.value);
            }}
            rows={3}
            maxLength={255}
          />
        </FormInput>

        <FormInput label="Customer email" description={FIELD_COPY.customerEmail} error={emailError}>
          <input
            ref={formRefs.customerEmail}
            type="email"
            value={formData.customerEmail}
            onChange={(event) => onUpdateFormData("customerEmail", event.target.value)}
            autoComplete="email"
            required
          />
        </FormInput>

        <div className="payfast-checkout-step__grid">
          <FormInput label="First name" description={FIELD_COPY.customerFirstName} error={firstNameError}>
            <input
              ref={formRefs.customerFirstName}
              type="text"
              value={formData.customerFirstName}
              onChange={(event) => onUpdateFormData("customerFirstName", event.target.value)}
              autoComplete="given-name"
              required
            />
          </FormInput>

          <FormInput label="Last name" description={FIELD_COPY.customerLastName} error={lastNameError}>
            <input
              ref={formRefs.customerLastName}
              type="text"
              value={formData.customerLastName}
              onChange={(event) => onUpdateFormData("customerLastName", event.target.value)}
              autoComplete="family-name"
              required
            />
          </FormInput>
        </div>

        <div className={`form-input ${agreeToTermsError ? "form-input--error" : ""}`}>
          <label className="form-input__label">
            <span>Payment authorization</span>
          </label>
          <div className="form-input__control">
            <label className="checkbox">
              <input
                ref={formRefs.agreeToTerms}
                type="checkbox"
                checked={formData.agreeToTerms}
                onChange={(event) => onUpdateFormData("agreeToTerms", event.target.checked)}
                required
              />
              <span>
                I confirm the customer information is accurate and I&apos;m authorized to initiate this payment session.
              </span>
            </label>
          </div>
          {agreeToTermsError && (
            <p className="form-input__error" role="alert">
              {agreeToTermsError}
            </p>
          )}
        </div>

        <div className="payfast-checkout-step__actions">
          <button type="submit" className="btn btn--primary" disabled={!isValid}>
            Continue
          </button>
          <button type="button" className="btn btn--ghost" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>

      <SecurityEventList />
    </section>
  );
};

export default PayFastCheckout;
