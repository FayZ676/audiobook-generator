import type { Meta, StoryObj } from "@storybook/react";

import AudioRecorder from "../app/components/audio/AudioRecorder";

const meta: Meta<typeof AudioRecorder> = {
  title: "Components/AudioRecorder",
  component: AudioRecorder,
  parameters: {
    layout: "padded",
  },
  args: {
    onRecordingComplete: (file: File) => {
      console.log("Recording completed:", file.name, file.size, "bytes");
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    maxDuration: 12,
  },
  render: (args) => (
    <div className="max-w-lg">
      <AudioRecorder {...args} />
    </div>
  ),
};

export const ShortDuration: Story = {
  args: {
    maxDuration: 5,
  },
  render: (args) => (
    <div className="max-w-lg">
      <h3 className="mb-4 text-lg font-semibold">5-second recording limit</h3>
      <AudioRecorder {...args} />
    </div>
  ),
};

export const LongDuration: Story = {
  args: {
    maxDuration: 30,
  },
  render: (args) => (
    <div className="max-w-lg">
      <h3 className="mb-4 text-lg font-semibold">30-second recording limit</h3>
      <AudioRecorder {...args} />
    </div>
  ),
};
