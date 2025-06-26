import type { Meta, StoryObj } from "@storybook/react";

import VoiceAddForm from "../app/components/VoiceAddForm";

const meta: Meta<typeof VoiceAddForm> = {
  title: "Components/VoiceAddForm",
  component: VoiceAddForm,
  parameters: {
    layout: "padded",
    docs: {
      description: {
        component: "A form for adding new voice samples, with options to either upload an audio file or record directly in the browser.",
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <div className="max-w-2xl mx-auto">
      <h2 className="mb-4 text-xl font-bold">Add New Voice</h2>
      <VoiceAddForm />
    </div>
  ),
};

export const InContainer: Story = {
  render: () => (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <h2 className="mb-6 text-2xl font-bold text-center">Voice Configuration</h2>
        <VoiceAddForm />
      </div>
    </div>
  ),
};