import type { Meta, StoryObj } from "@storybook/react";
import NarrationProgress from "../app/components/NarrationProgress";
import { Script } from "../app/actions/script";

const sampleScript: Script = [
  {
    voice_name: "narrator",
    speaker: {
      names: ["Narrator"],
      age: "middle-aged",
      gender: "male",
    },
    text: "This is sample text.",
  },
  {
    voice_name: "knight",
    speaker: {
      names: ["Sir Galahad"],
      age: "young",
      gender: "male",
    },
    text: "I shall face whatever dangers lie ahead, for honor and justice guide my path. No darkness can extinguish the light of righteousness that burns within my heart.",
  },
];

const meta: Meta<typeof NarrationProgress> = {
  title: "Components/NarrationProgress",
  component: NarrationProgress,
  parameters: {
    layout: "padded",
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    script: sampleScript,
  },
};

export const WithServerTimestamp: Story = {
  args: {
    script: sampleScript,
    narrationStartedAt: new Date(Date.now() - 30000).toISOString(), // 30 seconds ago
  },
};
