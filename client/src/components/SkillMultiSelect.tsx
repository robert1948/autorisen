import { useMemo, useState } from "react";

type SkillMultiSelectProps = {
  value: string[];
  onChange: (next: string[]) => void;
  suggestions?: string[];
};

const DEFAULT_SUGGESTIONS = [
  "Python",
  "TypeScript",
  "React",
  "FastAPI",
  "SQL",
  "Docker",
  "Kubernetes",
  "AWS",
  "Machine Learning",
];

const SkillMultiSelect = ({ value, onChange, suggestions = DEFAULT_SUGGESTIONS }: SkillMultiSelectProps) => {
  const [input, setInput] = useState("");

  const filteredSuggestions = useMemo(
    () =>
      suggestions
        .filter((item) => !value.includes(item))
        .filter((item) => item.toLowerCase().includes(input.toLowerCase()))
        .slice(0, 5),
    [input, suggestions, value],
  );

  const addSkill = (skill: string) => {
    const trimmed = skill.trim();
    if (!trimmed || value.includes(trimmed)) return;
    onChange([...value, trimmed]);
    setInput("");
  };

  const removeSkill = (skill: string) => {
    onChange(value.filter((item) => item !== skill));
  };

  return (
    <div className="skill-multi-select">
      <div className="skill-multi-select__tags">
        {value.map((skill) => (
          <span key={skill} className="skill-tag">
            {skill}
            <button type="button" onClick={() => removeSkill(skill)} aria-label={`Remove ${skill}`}>
              ×
            </button>
          </span>
        ))}
      </div>
      <input
        value={input}
        onChange={(event) => setInput(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            addSkill(input);
          }
        }}
        placeholder="Add a skill and press Enter"
      />
      {filteredSuggestions.length > 0 && (
        <ul className="skill-multi-select__suggestions">
          {filteredSuggestions.map((item) => (
            <li key={item}>
              <button type="button" onClick={() => addSkill(item)}>
                {item}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SkillMultiSelect;
