import { useCallback, useEffect, useRef, useState } from "react";

export default function SearchFilter({
  onSearch,
  filterOptions,
  onFilter,
  placeholder = "Search…",
}) {
  const [inputValue, setInputValue] = useState("");
  const [filterValue, setFilterValue] = useState("");
  const debounceRef = useRef(null);

  const handleSearchChange = useCallback(
    (e) => {
      const val = e.target.value;
      setInputValue(val);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        onSearch(val);
      }, 300);
    },
    [onSearch]
  );

  const handleFilterChange = useCallback(
    (e) => {
      const val = e.target.value;
      setFilterValue(val);
      onFilter(val);
    },
    [onFilter]
  );

  const handleClear = useCallback(() => {
    setInputValue("");
    setFilterValue("");
    if (debounceRef.current) clearTimeout(debounceRef.current);
    onSearch("");
    if (onFilter) onFilter("");
  }, [onSearch, onFilter]);

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const hasValue = inputValue !== "" || filterValue !== "";

  return (
    <div className="flex flex-wrap items-center gap-3 mb-4">
      <div className="relative flex-1 min-w-48">
        <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-gray-400">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z"
            />
          </svg>
        </div>
        <input
          type="text"
          value={inputValue}
          onChange={handleSearchChange}
          placeholder={placeholder}
          className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
        />
      </div>

      {filterOptions && filterOptions.length > 0 && (
        <select
          value={filterValue}
          onChange={handleFilterChange}
          className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 bg-white text-gray-700"
        >
          <option value="">All statuses</option>
          {filterOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      )}

      {hasValue && (
        <button
          onClick={handleClear}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-lg border border-gray-300 hover:border-gray-400 bg-white transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          Clear
        </button>
      )}
    </div>
  );
}
