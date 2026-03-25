export default function Pagination({ total, skip, limit, onPageChange }) {
  if (total <= 0) return null;

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = Math.ceil(total / limit);
  const startItem = skip + 1;
  const endItem = Math.min(skip + limit, total);

  const getPageNumbers = () => {
    const pages = [];
    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
      return pages;
    }

    if (currentPage <= 3) {
      pages.push(1, 2, 3, 4, 5);
    } else if (currentPage >= totalPages - 2) {
      pages.push(totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
    } else {
      pages.push(currentPage - 2, currentPage - 1, currentPage, currentPage + 1, currentPage + 2);
    }

    return pages;
  };

  const pageNumbers = getPageNumbers();
  const showStartEllipsis = totalPages > 5 && pageNumbers[0] > 1;
  const showEndEllipsis = totalPages > 5 && pageNumbers[pageNumbers.length - 1] < totalPages;

  const goToPage = (page) => {
    onPageChange((page - 1) * limit);
  };

  const btnBase =
    "px-3 py-1.5 text-sm rounded border transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500";
  const btnActive = "bg-brand-600 text-white border-brand-600 font-semibold";
  const btnInactive = "bg-white text-gray-700 border-gray-300 hover:bg-gray-50";
  const btnDisabled = "bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed";

  return (
    <div className="flex items-center justify-between mt-4 flex-wrap gap-2">
      <p className="text-sm text-gray-500">
        Showing <span className="font-medium text-gray-700">{startItem}</span>–
        <span className="font-medium text-gray-700">{endItem}</span> of{" "}
        <span className="font-medium text-gray-700">{total}</span> results
      </p>

      <div className="flex items-center gap-1">
        <button
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage === 1}
          className={`${btnBase} ${currentPage === 1 ? btnDisabled : btnInactive}`}
        >
          Previous
        </button>

        {showStartEllipsis && (
          <>
            <button onClick={() => goToPage(1)} className={`${btnBase} ${btnInactive}`}>
              1
            </button>
            <span className="px-2 text-gray-400 text-sm select-none">…</span>
          </>
        )}

        {pageNumbers.map((page) => (
          <button
            key={page}
            onClick={() => goToPage(page)}
            className={`${btnBase} ${page === currentPage ? btnActive : btnInactive}`}
          >
            {page}
          </button>
        ))}

        {showEndEllipsis && (
          <>
            <span className="px-2 text-gray-400 text-sm select-none">…</span>
            <button onClick={() => goToPage(totalPages)} className={`${btnBase} ${btnInactive}`}>
              {totalPages}
            </button>
          </>
        )}

        <button
          onClick={() => goToPage(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={`${btnBase} ${currentPage === totalPages ? btnDisabled : btnInactive}`}
        >
          Next
        </button>
      </div>
    </div>
  );
}
