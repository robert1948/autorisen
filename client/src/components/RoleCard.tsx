type RoleCardProps = {
  role: "Customer" | "Developer";
  title: string;
  description: string;
  selected: boolean;
  onSelect: (role: "Customer" | "Developer") => void;
  infoLink?: string;
};

const RoleCard = ({ role, title, description, selected, onSelect, infoLink }: RoleCardProps) => (
  <button
    type="button"
    className={`role-card ${selected ? "role-card--selected" : ""}`}
    onClick={() => onSelect(role)}
  >
    <h3>{title}</h3>
    <p>{description}</p>
    {infoLink && (
      <a
        href={infoLink}
        target="_blank"
        rel="noopener noreferrer"
        className="role-card__info-link"
        onClick={(e) => e.stopPropagation()}
      >
        Learn more &rarr;
      </a>
    )}
  </button>
);

export default RoleCard;
