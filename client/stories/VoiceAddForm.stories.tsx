import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";

import VoiceAddModal from "../app/components/voices/VoiceAddModal";

const meta: Meta<typeof VoiceAddModal> = {
  title: "Components/VoiceAddModal",
  component: VoiceAddModal,
  parameters: {
    layout: "padded",
    docs: {
      description: {
        component:
          "A modal for adding new voice samples, with options to either upload an audio file or record directly in the browser.",
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => {
    const [isOpen, setIsOpen] = useState(true);

    return (
      <div className="max-w-2xl mx-auto">
        <button
          onClick={() => setIsOpen(true)}
          className="btn btn-primary mb-4"
        >
          Open Voice Add Modal
        </button>
        <VoiceAddModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
      </div>
    );
  },
};

export const InContainer: Story = {
  render: () => {
    const [isOpen, setIsOpen] = useState(true);

    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
          <h2 className="mb-6 text-2xl font-bold text-center">
            Voice Configuration
          </h2>
          <button onClick={() => setIsOpen(true)} className="btn btn-primary">
            Add New Voice
          </button>
          <VoiceAddModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
        </div>
      </div>
    );
  },
};
