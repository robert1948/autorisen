import { ReactNode } from "react";

type FormInputProps = {
  label: string;
  description?: string;
  error?: string;
  children: ReactNode;
};

const FormInput = ({ label, description, error, children }: FormInputProps) => (
  <div className={`form-input ${error ? "form-input--error" : ""}`}>
    <label className="form-input__label">
      <span>{label}</span>
      {description && <span className="form-input__description">{description}</span>}
    </label>
    <div className="form-input__control">{children}</div>
    {error && <p className="form-input__error" role="alert">{error}</p>}
  </div>
);

export default FormInput;
