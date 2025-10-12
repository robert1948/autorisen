import ChatModal, { ChatPlacement } from "./ChatModal";

type Props = {
  open: boolean;
  onClose: () => void;
  placement?: Extract<ChatPlacement, "support" | "onboarding">;
};

const ChatSupport = ({ open, onClose, placement = "support" }: Props) => (
  <ChatModal
    open={open}
    onClose={onClose}
    placement={placement}
    title={placement === "support" ? "Talk with Support" : "CapeAI Onboarding Guide"}
    description={
      placement === "support"
        ? "Get real-time help from the CapeControl team—account help, features, or troubleshooting."
        : "Walk through your first tasks with CapeAI. Ask questions and get interactive guidance."
    }
  />
);

export default ChatSupport;
