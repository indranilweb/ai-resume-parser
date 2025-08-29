import React from 'react';
import { Folder, ArrowRight } from 'lucide-react';

interface FolderSelectionProps {
  folderPath: string;
  onFolderPathChange: (path: string) => void;
  onProceed: () => void;
}

const FolderSelection: React.FC<FolderSelectionProps> = ({
  folderPath,
  onFolderPathChange,
  onProceed,
}) => {
  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Extract the folder path from the first file's webkitRelativePath
      const path = files[0].webkitRelativePath.split('/')[0];
      onFolderPathChange(path);
    } else {
      onFolderPathChange('No folder selected...');
    }
  };

  return (
    <div className="space-y-4">
      <label htmlFor="folder-path" className="block text-sm font-medium text-gray-100 mb-3">
        <span className="flex items-center space-x-3">
          <span className="w-6 h-6 bg-blue-600 text-white rounded-md text-xs flex items-center justify-center font-semibold">
            1
          </span>
          <Folder className="text-blue-400 w-4 h-4" />
          <span>Enter Resume Folder Path</span>
        </span>
      </label>
      <div className="flex space-x-3">
        <input
          type="text"
          id="folder-path"
          value={folderPath}
          onChange={(e) => onFolderPathChange(e.target.value)}
          className="flex-1 bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-gray-100 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm font-mono"
          placeholder="No folder selected..."
        />
        <button
          onClick={onProceed}
          disabled={!folderPath || folderPath === 'No folder selected...'}
          className="px-4 py-2 bg-gray-700 text-blue-500 text-sm font-medium rounded-md hover:bg-blue-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors flex items-center space-x-2 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed disabled:hover:bg-gray-700 disabled:hover:text-gray-500"
        >
          <ArrowRight className="w-4 h-4" />
          <span>Proceed</span>
        </button>
      </div>
      <input
        type="file"
        id="folder-input"
        // @ts-ignore - webkitdirectory is not in standard HTMLInputElement types
        webkitdirectory=""
        multiple
        className="hidden"
        onChange={handleFileInputChange}
      />
    </div>
  );
};

export default FolderSelection;
