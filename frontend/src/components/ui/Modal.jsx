export default function Modal({ children }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-lg">
        {children}
      </div>
    </div>
  );
}
