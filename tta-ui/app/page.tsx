"use client";

import React, { useState, ChangeEvent } from "react";
import type { NextPage } from "next";

const Home: NextPage = () => {
  const [fileName, setFileName] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<string>("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      setUploadResult(""); // Clear previous upload result when new file is selected
    } else {
      setFileName("");
    }
  };

  const handleUpload = () => {
    setIsLoading(true);
    // Simulate an upload process
    setTimeout(() => {
      setIsLoading(false);
      setUploadResult(`File "${fileName}" uploaded successfully!`);
      setFileName(""); // Reset the file name after upload
      // Reset the file input
      const fileInput = document.querySelector(
        'input[type="file"]'
      ) as HTMLInputElement;
      if (fileInput) fileInput.value = "";
    }, 3000); // 3 seconds delay to simulate upload
  };

  return (
    <main className="flex flex-col items-start gap-2 p-4">
      <input
        type="file"
        className="file-input file-input-bordered w-full max-w-xs"
        onChange={handleFileChange}
        disabled={isLoading}
      />
      {fileName && <p className="mt-2">Selected file: {fileName}</p>}
      <button
        className="btn"
        onClick={handleUpload}
        disabled={!fileName || isLoading}
      >
        {isLoading ? (
          <>
            <span className="loading loading-spinner"></span>
            uploading
          </>
        ) : (
          "Upload"
        )}
      </button>
      {uploadResult && <p className="mt-2 text-green-600">{uploadResult}</p>}
    </main>
  );
};

export default Home;
