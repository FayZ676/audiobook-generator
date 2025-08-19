import type { Meta, StoryObj } from "@storybook/react";

import AudioPlayerLarge from "../app/components/audio/AudioPlayerLarge";

const meta: Meta<typeof AudioPlayerLarge> = {
  title: "Components/AudioPlayerLarge",
  component: AudioPlayerLarge,
  parameters: {
    layout: "padded",
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    src: "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwE",
  },
  render: (args) => <AudioPlayerLarge {...args} />,
};

export const Disabled: Story = {
  args: {
    src: "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwEJHfH8N2QQAoUXrTp66hVFApGn+DyvmUgAy1+0fPWeiwE",
    disabled: true,
  },
  render: (args) => <AudioPlayerLarge {...args} />,
};

export const NoAudio: Story = {
  args: {
    src: "",
  },
  render: (args) => <AudioPlayerLarge {...args} />,
};