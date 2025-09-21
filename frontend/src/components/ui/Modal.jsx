export default function Modal({ children, isOpen = true, onClose = () => {}, title }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      {/* Overlay: clicking it closes the modal */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg max-w-3xl w-full mx-4">
        {/* Header with optional title and close button */}
        <div className="flex items-start justify-between mb-4">
          {title ? (
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
          ) : (
            <div />
          )}
          <button
            type="button"
            aria-label="Close modal"
            className="p-2 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            onClick={onClose}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <div onClick={(e) => e.stopPropagation()}>
          {children}
        </div>
      </div>
    </div>
  );
}
