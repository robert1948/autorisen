type RoleCardProps = {
  role: "Customer" | "Developer";
  title: string;
  description: string;
  selected: boolean;
  onSelect: (role: "Customer" | "Developer") => void;
};

const RoleCard = ({ role, title, description, selected, onSelect }: RoleCardProps) => (
  <button
    type="button"
    className={`role-card ${selected ? "role-card--selected" : ""}`}
    onClick={() => onSelect(role)}
  >
    <h3>{title}</h3>
    <p>{description}</p>
  </button>
);

export default RoleCard;
