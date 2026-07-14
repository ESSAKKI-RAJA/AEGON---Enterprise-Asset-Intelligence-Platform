import { useState, useRef } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  SortingState,
  RowSelectionState,
} from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import {
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  Download,
  Search,
  AlertCircle,
  CheckSquare,
  Square,
  Trash2,
  Archive,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  title?: string;
  icon?: React.ReactNode;
  exportable?: boolean;
  searchable?: boolean;
  selectable?: boolean;
  isLoading?: boolean;
  error?: Error | null;
  filename?: string;
  virtualized?: boolean;
  onSelectionAction?: (action: string, selectedRows: TData[]) => void;
}

export function DataTable<TData, TValue>({
  columns: userColumns,
  data,
  title,
  icon,
  exportable = false,
  searchable = false,
  selectable = false,
  isLoading = false,
  error = null,
  filename = "export",
  virtualized = false,
  onSelectionAction,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});

  // Inject selection column if enabled
  const columns = selectable
    ? [
        {
          id: "select",
          header: ({ table }: any) => (
            <button
              onClick={table.getToggleAllRowsSelectedHandler()}
              className="grid h-4 w-4 place-items-center rounded border border-slate-300 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-indigo-500"
            >
              {table.getIsAllRowsSelected() ? (
                <CheckSquare className="h-4 w-4 text-indigo-500 dark:text-indigo-400" />
              ) : table.getIsSomeRowsSelected() ? (
                <div className="h-2 w-2 bg-indigo-500 rounded-sm" />
              ) : (
                <Square className="h-4 w-4 text-transparent" />
              )}
            </button>
          ),
          cell: ({ row }: any) => (
            <button
              onClick={row.getToggleSelectedHandler()}
              className="grid h-4 w-4 place-items-center rounded border border-slate-300 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {row.getIsSelected() ? (
                <CheckSquare className="h-4 w-4 text-indigo-500 dark:text-indigo-400" />
              ) : (
                <Square className="h-4 w-4 text-transparent" />
              )}
            </button>
          ),
          size: 40,
        },
        ...userColumns,
      ]
    : userColumns;

  const table = useReactTable({
    data,
    columns: columns as ColumnDef<TData, TValue>[],
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onGlobalFilterChange: setGlobalFilter,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      globalFilter,
      rowSelection,
    },
  });

  const { rows } = table.getRowModel();
  const tableContainerRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 48,
    overscan: 10,
  });

  const handleExport = () => {
    const headers = columns.map((c) => (c.header as string) || c.id).filter(Boolean);
    const exportRows = table.getFilteredRowModel().rows.map((row) => {
      return columns
        .map((col) => {
          const val = row.getValue(col.id as string) ?? "";
          return `"${String(val).replace(/"/g, '""')}"`;
        })
        .join(",");
    });

    const csvContent = [headers.join(","), ...exportRows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${filename}_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Use a custom event to trigger toast since toast is from sonner and might not be imported directly here
    // Wait, let's just import toast.
    import("sonner").then(({ toast }) => {
      toast.success(`${filename} exported successfully.`);
    });
  };

  const selectedRowsCount = Object.keys(rowSelection).length;
  const isFloatingActionBarVisible = selectable && selectedRowsCount > 0;

  return (
    <div className="relative rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden flex flex-col h-full shadow-sm">
      {(title || icon || exportable || searchable) && (
        <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex flex-wrap gap-4 justify-between items-center shrink-0 backdrop-blur-md">
          <div className="flex items-center gap-2.5">
            {icon && (
              <div className="text-indigo-600 dark:text-indigo-400 p-1.5 bg-indigo-50 dark:bg-indigo-500/10 rounded-lg">
                {icon}
              </div>
            )}
            {title && (
              <h3 className="text-[15px] font-bold text-slate-900 dark:text-slate-100 font-sans tracking-tight">
                {title}
              </h3>
            )}
          </div>

          <div className="flex items-center gap-3 ml-auto">
            {searchable && (
              <div className="relative">
                <Search className="absolute left-3 top-2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Filter records..."
                  value={globalFilter ?? ""}
                  onChange={(e) => setGlobalFilter(e.target.value)}
                  className="bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-200 text-sm rounded-lg pl-9 pr-4 py-1.5 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 w-64 transition-all shadow-sm"
                />
              </div>
            )}

            {exportable && (
              <button
                onClick={handleExport}
                disabled={data.length === 0 || isLoading || !!error}
                className="text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1.5 flex items-center gap-2 transition-colors disabled:opacity-50 shadow-sm disabled:shadow-none"
              >
                <Download className="h-4 w-4 text-slate-400" /> Export
              </button>
            )}
          </div>
        </div>
      )}

      <div
        ref={tableContainerRef}
        className="overflow-auto flex-1 custom-scrollbar min-h-[300px] relative"
      >
        <table className="w-full text-left text-sm font-sans text-slate-600 dark:text-slate-300">
          <thead className="bg-slate-50/95 dark:bg-slate-900/95 text-xs text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10 backdrop-blur-md">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <th
                      key={header.id}
                      style={{ width: header.getSize() }}
                      className={cn(
                        "px-5 py-3.5 font-semibold transition-colors whitespace-nowrap",
                        header.column.getCanSort()
                          ? "cursor-pointer select-none hover:text-slate-900 dark:hover:text-slate-200"
                          : "",
                      )}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      <div className="flex items-center gap-2">
                        {header.isPlaceholder
                          ? null
                          : flexRender(header.column.columnDef.header, header.getContext())}
                        {{
                          asc: <ChevronUp className="h-4 w-4 inline text-indigo-500" />,
                          desc: <ChevronDown className="h-4 w-4 inline text-indigo-500" />,
                        }[header.column.getIsSorted() as string] ?? null}
                      </div>
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>

          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {isLoading ? (
              // Skeleton Loader
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  {columns.map((c, j) => (
                    <td key={j} className="px-5 py-4">
                      <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-full max-w-[80%]"></div>
                    </td>
                  ))}
                </tr>
              ))
            ) : error ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="h-32 text-center text-red-600 dark:text-red-400/80 bg-red-50 dark:bg-red-950/10"
                >
                  <div className="flex flex-col items-center justify-center gap-2">
                    <AlertCircle className="h-5 w-5" />
                    <span className="text-sm font-medium">
                      {error.message || "Failed to load enterprise data"}
                    </span>
                  </div>
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="h-32 text-center text-slate-500">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <span className="text-sm">No matching records found.</span>
                  </div>
                </td>
              </tr>
            ) : virtualized ? (
              // Virtualized rendering
              <>
                <tr
                  style={{
                    height: `${rowVirtualizer.getTotalSize()}px`,
                    display: "block",
                    position: "relative",
                  }}
                >
                  {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                    const row = rows[virtualRow.index];
                    return (
                      <tr
                        key={row.id}
                        style={{
                          position: "absolute",
                          top: 0,
                          left: 0,
                          width: "100%",
                          transform: `translateY(${virtualRow.start}px)`,
                        }}
                        className={cn(
                          "hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors group flex",
                          row.getIsSelected() && "bg-indigo-50/50 dark:bg-indigo-900/10",
                        )}
                      >
                        {row.getVisibleCells().map((cell) => (
                          <td
                            key={cell.id}
                            style={{ width: cell.column.getSize() }}
                            className="px-5 py-3 whitespace-nowrap flex-1"
                          >
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tr>
              </>
            ) : (
              // Standard rendering
              rows.map((row) => (
                <tr
                  key={row.id}
                  className={cn(
                    "hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors group",
                    row.getIsSelected() && "bg-indigo-50/50 dark:bg-indigo-900/10",
                  )}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-5 py-3 whitespace-nowrap">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {table.getPageCount() > 1 && (
        <div className="px-5 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex items-center justify-between shrink-0">
          <div className="text-xs text-slate-500 font-medium">
            Showing{" "}
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}
            </span>{" "}
            to{" "}
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              {Math.min(
                (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
                data.length,
              )}
            </span>{" "}
            of{" "}
            <span className="font-semibold text-slate-700 dark:text-slate-300">{data.length}</span>{" "}
            entries
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="p-1.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white disabled:opacity-50 text-slate-500 transition-colors shadow-sm"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="p-1.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white disabled:opacity-50 text-slate-500 transition-colors shadow-sm"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Floating Action Bar */}
      <AnimatePresence>
        {isFloatingActionBarVisible && (
          <motion.div
            initial={{ y: 50, opacity: 0, x: "-50%" }}
            animate={{ y: 0, opacity: 1, x: "-50%" }}
            exit={{ y: 50, opacity: 0, x: "-50%" }}
            className="absolute bottom-6 left-1/2 flex items-center gap-4 bg-slate-900 dark:bg-slate-800 text-white px-5 py-3 rounded-full shadow-2xl border border-slate-700 z-50 backdrop-blur-md"
          >
            <span className="text-sm font-medium mr-2">
              <span className="font-bold">{selectedRowsCount}</span>{" "}
              {selectedRowsCount === 1 ? "row" : "rows"} selected
            </span>
            <div className="w-px h-5 bg-slate-700"></div>
            <button
              onClick={() =>
                onSelectionAction?.(
                  "delete",
                  table.getSelectedRowModel().rows.map((r) => r.original),
                )
              }
              className="flex items-center gap-1.5 text-sm font-medium hover:text-red-400 transition-colors"
            >
              <Trash2 className="h-4 w-4" /> Delete
            </button>
            <button
              onClick={() =>
                onSelectionAction?.(
                  "archive",
                  table.getSelectedRowModel().rows.map((r) => r.original),
                )
              }
              className="flex items-center gap-1.5 text-sm font-medium hover:text-amber-400 transition-colors"
            >
              <Archive className="h-4 w-4" /> Archive
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
