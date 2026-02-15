type Props = {
  onLaunchChat: () => void;
};

const AgentWorkbench = ({ onLaunchChat }: Props) => (
  <article className="experience-card">
    <div className="experience-card__header">
      <span className="badge">Developer Workbench</span>
      <h3>Test and iterate with live logs</h3>
    </div>
    <p>
      Prototype prompts, inspect tool calls, and replay golden tasks in the ChatKit-powered workbench.
      Ship confidently with built-in telemetry and regression checks before publishing to the
      marketplace.
    </p>
    <ul className="experience-card__steps">
      <li>Load agent &amp; tool manifest</li>
      <li>Chat, inspect traces, tweak prompts</li>
      <li>Promote successful runs into recipes</li>
    </ul>
    <div className="experience-card__actions">
      <button type="button" className="btn btn--ghost" onClick={onLaunchChat}>
        Open Agent Workbench
      </button>
      <a className="btn btn--link" href="/developers">
        View developer docs →
      </a>
    </div>
  </article>
);

export default AgentWorkbench;
