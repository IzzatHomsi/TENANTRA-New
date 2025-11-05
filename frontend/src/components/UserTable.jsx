const UserTable = ({ users, onEdit, onDelete }) => {
  // The UserTable component renders a table of user information.
  // - users: array of user objects to display
  // - onEdit: callback invoked with the user object when the edit button is clicked
  // - onDelete: callback invoked with the user's id when the delete button is clicked

  // Wrap the table in a div that allows horizontal scrolling on small screens. This
  // ensures the layout remains usable when the table width exceeds the viewport.
  return (
    <div className="overflow-x-auto">
      {/* The main table element uses Tailwind CSS classes for styling: full width,
          white background, border and row dividers. */}
      <table className="min-w-full bg-white border border-gray-300 divide-y divide-gray-200">
        {/* Table header: set a light background and uppercase labels for clarity. */}
        <thead className="bg-gray-50">
          <tr>
            {/* Each <th> defines a column header. We apply padding and text styling. */}
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Username</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Active</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        {/* Table body: iterate over the users array to generate rows. Rows are
            separated by dividing lines for better readability. */}
        <tbody className="bg-white divide-y divide-gray-200">
          {users.map((user) => (
            // Use the user's id as the key to help React identify rows.
            <tr key={user.id} className="hover:bg-gray-50">
              {/* Display the user's id. The whitespace-nowrap class prevents text wrapping. */}
              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">{user.id}</td>
              {/* Display the user's username. */}
              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">{user.username}</td>
              {/* Display the user's email. */}
              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">{user.email}</td>
              {/* Display the user's role. Replace underscores with spaces and capitalize
                  for better presentation. */}
              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700 capitalize">{user.role.replace(/_/g, ' ')}</td>
              {/* Show whether the user is active. */}
              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">{user.is_active ? 'Yes' : 'No'}</td>
              {/* Actions column: provides Edit and Delete buttons. The space-x-2
                  class adds horizontal spacing between the buttons. */}
              <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700 space-x-2">
                {/* Clicking the Edit button calls onEdit with the current user
                    object. Styling colors the link blue and darkens on hover. */}
                <button
                  onClick={() => onEdit(user)}
                  className="text-blue-600 hover:text-blue-900 focus:outline-none"
                >
                  Edit
                </button>
                {/* Clicking the Delete button calls onDelete with the user's id. Styling
                    colors the link red and darkens on hover. */}
                <button
                  onClick={() => onDelete(user.id)}
                  className="text-red-600 hover:text-red-900 focus:outline-none"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserTable;