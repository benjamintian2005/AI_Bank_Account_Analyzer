import { useState } from "react";

export default function BankStatementUpload() {
  const [file, setFile] = useState(null);
  const [output, setOutput] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error("Failed to upload file");
      }
      
      const data = await response.json();
      setOutput(data.result);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Upload failed: " + error.message);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-lg">
        <h2 className="text-2xl font-semibold mb-4 text-center">Upload PDF for AI Analysis</h2>
        <div className="border-2 border-dashed border-gray-300 p-4 text-center rounded-lg">
          <input type="file" onChange={handleFileChange} accept=".pdf" className="hidden" id="file-upload" />
          <label htmlFor="file-upload" className="cursor-pointer text-blue-600 hover:underline">Choose a PDF</label>
        </div>
        <button 
          className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition" 
          onClick={handleUpload}>
          Upload & Analyze
        </button>
        {output && (
          <div className="mt-6 p-4 bg-gray-50 border border-gray-300 rounded-lg">
            <h3 className="text-lg font-semibold text-center text-gray-700">AI Summary</h3>
            <div className="mt-2 p-3 bg-white rounded shadow-sm text-gray-800">
              <p className="whitespace-pre-line">{output}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
