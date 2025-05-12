// src/components/Modal.jsx
import React from "react";

export default function Modal({ onClose, title, children }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="bg-[#1f1f1f] w-full max-w-2xl p-6 rounded-xl shadow-xl relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-white bg-red-500 hover:bg-red-600 px-3 py-1 rounded"
        >
          Close
        </button>
        <h2 className="text-2xl font-bold text-red-400 mb-4">{title}</h2>
        <div className="text-gray-300 space-y-2">{children}</div>
      </div>
    </div>
  );
}
