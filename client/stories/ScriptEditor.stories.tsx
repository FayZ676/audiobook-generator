import type { Meta, StoryObj } from "@storybook/react";

import ScriptEditor from "@/app/components/script/ScriptEditor";
import { Script } from "@/app/actions/script";
import { Voice } from "@/app/actions/voices";

const sampleScript: Script = {
  segments: [
    {
      text: "Once upon a time, in a land far, far away, there lived a brave knight.",
      speaker_alias: "narrator",
    },
    {
      text: "I shall face whatever dangers lie ahead, for honor and justice guide my path. No darkness can extinguish the light of righteousness that burns within my heart.",
      speaker_alias: "knight",
    },
    {
      text: "Thank you, brave knight, for saving our kingdom from the terrible dragon!",
      speaker_alias: "princess",
    },
  ],
  speakers: [
    {
      names: ["Narrator"],
      age: "middle-aged",
      gender: "male",
      voice_name: "narrator_voice",
      audio_path: "",
      audio_transcript: "",
    },
    {
      names: ["Sir Galahad"],
      age: "young",
      gender: "male",
      voice_name: "knight_voice",
      audio_path: "",
      audio_transcript: "",
    },
    {
      names: ["Princess Elara"],
      age: "young",
      gender: "female",
      voice_name: "princess_voice",
      audio_path: "",
      audio_transcript: "",
    },
  ],
};

const sampleVoices: Voice[] = [
  {
    name: "narrator_voice",
    age: "middle-aged",
    gender: "male",
    audio_path: "/audio/narrator.mp3",
    audio_transcript: "Sample narrator voice",
  },
  {
    name: "knight_voice",
    age: "young",
    gender: "male",
    audio_path: "/audio/knight.mp3",
    audio_transcript: "Sample knight voice",
  },
  {
    name: "princess_voice",
    age: "young",
    gender: "female",
    audio_path: "/audio/princess.mp3",
    audio_transcript: "Sample princess voice",
  },
  {
    name: "wizard_voice",
    age: "old",
    gender: "male",
    audio_path: "/audio/wizard.mp3",
    audio_transcript: "Sample wizard voice",
  },
  {
    name: "maiden_voice",
    age: "young",
    gender: "female",
    audio_path: "/audio/maiden.mp3",
    audio_transcript: "Sample maiden voice",
  },
];

const meta: Meta<typeof ScriptEditor> = {
  title: "Components/ScriptEditor",
  component: ScriptEditor,
  parameters: {
    layout: "padded",
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    script: sampleScript,
    voices: sampleVoices,
  },
  render: (args) => <ScriptEditor {...args} />,
};

export const EmptyScript: Story = {
  args: {
    script: { segments: [], speakers: [] },
    voices: sampleVoices,
  },
  render: (args) => <ScriptEditor {...args} />,
};
