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
    text: "Once upon a time, in a land far away, there lived a brave knight who embarked on an epic adventure. The journey was long and filled with challenges that tested both courage and wisdom.",
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
