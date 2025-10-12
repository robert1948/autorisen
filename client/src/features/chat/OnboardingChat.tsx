type Props = {
  onLaunchChat: () => void;
};

const OnboardingChat = ({ onLaunchChat }: Props) => (
  <article className="experience-card">
    <div className="experience-card__header">
      <span className="badge">CapeAI Guide</span>
      <h3>Personalized onboarding in minutes</h3>
    </div>
    <p>
      Answer a few natural-language questions and CapeAI builds a launch checklist tailored to your
      tenant, data sources, and goals. You can save progress, invite teammates, and hand off tasks
      straight from chat.
    </p>
    <ul className="experience-card__steps">
      <li>Goal intake → clarify constraints</li>
      <li>Generate plan → validate with you</li>
      <li>Execute tasks → track outcomes</li>
    </ul>
    <button type="button" className="btn btn--primary" onClick={onLaunchChat}>
      Start CapeAI Onboarding
    </button>
  </article>
);

export default OnboardingChat;
