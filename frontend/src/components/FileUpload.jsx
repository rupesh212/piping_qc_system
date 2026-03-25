import { useRef, useState } from "react";

export default function FileUpload({ onUpload, accept, label, loading }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState(null);

  const handleFile = (file) => {
    if (!file) return;
    setFileName(file.name);
    onUpload(file);
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        dragging ? "border-brand-500 bg-blue-50" : "border-gray-300 hover:border-brand-500"
      }`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFile(e.dataTransfer.files[0]);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={accept}
        onChange={(e) => handleFile(e.target.files[0])}
      />
      {loading ? (
        <p className="text-brand-600 font-medium">Uploading & processing...</p>
      ) : (
        <>
          <p className="text-gray-600">{label || "Click or drag & drop a file here"}</p>
          {fileName && <p className="mt-2 text-sm text-brand-600 font-medium">{fileName}</p>}
        </>
      )}
    </div>
  );
}
