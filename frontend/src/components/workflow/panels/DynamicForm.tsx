interface FieldSchema {
  key: string;
  label: string;
  type: "string" | "text" | "number" | "boolean" | "select";
  description?: string;
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: string }[];
}

interface DynamicFormProps {
  schema: FieldSchema[];
  values: Record<string, any>;
  onChange: (values: Record<string, any>) => void;
}

/**
 * DynamicForm - Renders a form based on a schema definition
 * Supports: string, text, number, boolean, select field types
 */
export default function DynamicForm({
  schema,
  values,
  onChange,
}: DynamicFormProps) {
  const handleFieldChange = (key: string, value: any) => {
    onChange({
      ...values,
      [key]: value,
    });
  };

  return (
    <div className="space-y-4">
      {schema.map((field) => (
        <div key={field.key} className="space-y-1.5">
          {/* Label */}
          <label className="block text-sm font-medium text-gray-300">
            {field.label}
            {field.required && <span className="text-red-400 ml-1">*</span>}
          </label>

          {/* Description */}
          {field.description && (
            <p className="text-xs text-gray-500">{field.description}</p>
          )}

          {/* Input Field */}
          {field.type === "string" && (
            <input
              type="text"
              value={values[field.key] || ""}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              placeholder={field.placeholder}
              required={field.required}
              className="
                w-full px-3 py-2 rounded-lg
                bg-gray-700 border-2 border-gray-600
                text-gray-200 placeholder-gray-500
                focus:outline-none focus:border-indigo-500
                transition-colors text-sm
              "
            />
          )}

          {field.type === "text" && (
            <textarea
              value={values[field.key] || ""}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              placeholder={field.placeholder}
              required={field.required}
              rows={4}
              className="
                w-full px-3 py-2 rounded-lg
                bg-gray-700 border-2 border-gray-600
                text-gray-200 placeholder-gray-500
                focus:outline-none focus:border-indigo-500
                transition-colors text-sm resize-vertical
              "
            />
          )}

          {field.type === "number" && (
            <input
              type="number"
              value={values[field.key] || ""}
              onChange={(e) =>
                handleFieldChange(field.key, parseFloat(e.target.value))
              }
              placeholder={field.placeholder}
              required={field.required}
              className="
                w-full px-3 py-2 rounded-lg
                bg-gray-700 border-2 border-gray-600
                text-gray-200 placeholder-gray-500
                focus:outline-none focus:border-indigo-500
                transition-colors text-sm
              "
            />
          )}

          {field.type === "boolean" && (
            <label className="flex items-center gap-3 cursor-pointer group">
              <div className="relative">
                <input
                  type="checkbox"
                  checked={values[field.key] || false}
                  onChange={(e) =>
                    handleFieldChange(field.key, e.target.checked)
                  }
                  className="sr-only peer"
                />
                <div
                  className="
                  w-11 h-6 bg-gray-600 rounded-full
                  peer-checked:bg-indigo-500
                  transition-colors
                "
                ></div>
                <div
                  className="
                  absolute left-1 top-1 w-4 h-4 bg-white rounded-full
                  peer-checked:translate-x-5
                  transition-transform
                "
                ></div>
              </div>
              <span className="text-sm text-gray-400 group-hover:text-gray-300">
                {values[field.key] ? "Enabled" : "Disabled"}
              </span>
            </label>
          )}

          {field.type === "select" && (
            <select
              value={values[field.key] || ""}
              onChange={(e) => handleFieldChange(field.key, e.target.value)}
              required={field.required}
              className="
                w-full px-3 py-2 rounded-lg
                bg-gray-700 border-2 border-gray-600
                text-gray-200
                focus:outline-none focus:border-indigo-500
                transition-colors text-sm
              "
            >
              <option value="">Select an option...</option>
              {field.options?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          )}
        </div>
      ))}

      {schema.length === 0 && (
        <p className="text-sm text-gray-500 text-center py-4">
          No fields to configure
        </p>
      )}
    </div>
  );
}
