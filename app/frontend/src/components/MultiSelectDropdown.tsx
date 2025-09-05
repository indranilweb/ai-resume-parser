import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface MultiSelectDropdownProps {
  options: string[];
  selectedOptions: string[];
  onSelectionChange: (selectedOptions: string[]) => void;
  placeholder?: string;
  label?: string;
  icon?: React.ReactNode;
}

const MultiSelectDropdown: React.FC<MultiSelectDropdownProps> = ({
  options,
  selectedOptions,
  onSelectionChange,
  placeholder = "Select options...",
  label,
  icon
}) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const [shouldOpenUpward, setShouldOpenUpward] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (isDropdownOpen && triggerRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      const dropdownHeight = options.length * 40 + 8; // Approximate height of dropdown
      const spaceBelow = viewportHeight - triggerRect.bottom;
      const spaceAbove = triggerRect.top;

      // Open upward if there's not enough space below but enough space above
      if (spaceBelow < dropdownHeight && spaceAbove > dropdownHeight) {
        setShouldOpenUpward(true);
      } else {
        setShouldOpenUpward(false);
      }
    }
  }, [isDropdownOpen, options.length]);

  const handleOptionToggle = (option: string) => {
    const newSelection = selectedOptions.includes(option)
      ? selectedOptions.filter(item => item !== option)
      : [...selectedOptions, option];
    
    onSelectionChange(newSelection);
  };

  const removeOption = (option: string) => {
    const newSelection = selectedOptions.filter(item => item !== option);
    onSelectionChange(newSelection);
  };

  return (
    <div className="space-y-4">
      {label && (
        <label className="block text-sm font-medium text-gray-100 mb-3">
          <span className="flex items-center space-x-3">
            {icon}
            <span>{label}</span>
          </span>
        </label>
      )}
      <div className="relative" ref={dropdownRef}>
        <div
          ref={triggerRef}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-md text-gray-100 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none text-sm cursor-pointer min-h-[38px] flex items-center justify-between"
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        >
          <div className="flex flex-wrap gap-1.5">
            {selectedOptions.length > 0 ? (
              selectedOptions.map((option) => (
                <span
                  key={option}
                  className="inline-flex items-center px-1.5 py-0.5 rounded-md text-xs font-medium bg-blue-600 text-white"
                >
                  {option}
                  <button
                    type="button"
                    className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full text-blue-200 hover:bg-blue-700 hover:text-white focus:outline-none"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeOption(option);
                    }}
                  >
                    ×
                  </button>
                </span>
              ))
            ) : (
              <span className="text-gray-400">{placeholder}</span>
            )}
          </div>
          <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isDropdownOpen ? 'transform rotate-180' : ''}`} />
        </div>
        
        {isDropdownOpen && (
          <div className={`absolute z-10 w-full bg-gray-900 border border-gray-700 rounded-md shadow-lg ${
            shouldOpenUpward ? 'bottom-full mb-1' : 'top-full mt-1'
          }`}>
            {options.map((option) => (
              <div
                key={option}
                className={`px-3 py-2 text-sm cursor-pointer hover:bg-gray-800 flex items-center space-x-2 ${
                  selectedOptions.includes(option) ? 'bg-gray-800' : ''
                }`}
                onClick={() => handleOptionToggle(option)}
              >
                <input
                  type="checkbox"
                  checked={selectedOptions.includes(option)}
                  onChange={() => {}} // Handled by onClick
                  className="w-4 h-4 text-blue-600 bg-gray-900 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                />
                <span className="text-gray-100">{option}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiSelectDropdown;
