const PASSWORD_REQUIREMENTS = [
  { test: (value: string) => value.length >= 12, label: "At least 12 characters" },
  { test: (value: string) => /[a-z]/.test(value), label: "Lowercase letter" },
  { test: (value: string) => /[A-Z]/.test(value), label: "Uppercase letter" },
  { test: (value: string) => /\d/.test(value), label: "Digit" },
  { test: (value: string) => /[^A-Za-z0-9]/.test(value), label: "Special character" },
];

type PasswordMeterProps = {
  password: string;
};

const PasswordMeter = ({ password }: PasswordMeterProps) => {
  const metCount = PASSWORD_REQUIREMENTS.filter((rule) => rule.test(password)).length;
  const percent = Math.round((metCount / PASSWORD_REQUIREMENTS.length) * 100);

  return (
    <div className="password-meter" aria-live="polite">
      <div className="password-meter__bar">
        <div className="password-meter__fill" style={{ width: `${percent}%` }} />
      </div>
      <ul className="password-meter__list">
        {PASSWORD_REQUIREMENTS.map((rule) => (
          <li key={rule.label} className={rule.test(password) ? "ok" : ""}>
            {rule.label}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PasswordMeter;
