
import React from 'react';
import { X, Copy, FileJson } from 'lucide-react';

interface JsonModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    data: any;
}

export const JsonModal: React.FC<JsonModalProps> = ({ isOpen, onClose, title, data }) => {
    if (!isOpen) return null;

    const handleCopy = () => {
        navigator.clipboard.writeText(JSON.stringify(data, null, 2));
        alert("JSON copiado al portapapeles");
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 rounded-lg shadow-2xl w-full max-w-4xl max-h-[80vh] flex flex-col">
                <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950 rounded-t-lg">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <FileJson className="w-5 h-5 text-blue-400" />
                        {title}
                    </h3>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleCopy}
                            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition-colors"
                            title="Copiar JSON"
                        >
                            <Copy className="w-5 h-5" />
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                <div className="flex-1 overflow-auto p-4 bg-slate-950 font-mono text-xs md:text-sm">
                    <pre className="text-slate-300 whitespace-pre-wrap break-words">
                        {JSON.stringify(data, null, 2)}
                    </pre>
                </div>

                <div className="p-4 border-t border-slate-800 bg-slate-900 rounded-b-lg flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-slate-800 text-white rounded hover:bg-slate-700 transition-colors"
                    >
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    );
};
