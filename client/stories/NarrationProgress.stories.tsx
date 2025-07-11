import type { Meta, StoryObj } from "@storybook/react";

import NarrationProgress from "../app/components/narration/NarrationProgress";
import { Script } from "../app/actions/script";

const sampleScript: Script = {
  segments: [
    {
      text: "This is sample text.",
      speaker_alias: "narrator",
    },
    {
      text: "I shall face whatever dangers lie ahead, for honor and justice guide my path. No darkness can extinguish the light of righteousness that burns within my heart.",
      speaker_alias: "knight",
    },
  ],
  speakers: [
    {
      names: ["Narrator"],
      age: "middle-aged",
      gender: "male",
      voice_name: "narrator",
      audio_path: "",
      audio_transcript: "",
    },
    {
      names: ["Sir Galahad"],
      age: "young",
      gender: "male",
      voice_name: "knight",
      audio_path: "",
      audio_transcript: "",
    },
  ],
};

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
  render: (args) => <NarrationProgress {...args} />,
};

export const WithServerTimestamp: Story = {
  args: {
    script: sampleScript,
    narrationStartedAt: new Date(Date.now() - 30000).toISOString(), // 30 seconds ago
  },
  render: (args) => <NarrationProgress {...args} />,
};
