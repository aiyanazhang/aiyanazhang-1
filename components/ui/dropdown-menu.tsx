import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronDown } from "lucide-react"

const DropdownMenu = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    trigger: React.ReactNode;
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
  }
>(({ className, trigger, children, open, onOpenChange, ...props }, ref) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  const actualOpen = open !== undefined ? open : isOpen;
  const setActualOpen = onOpenChange || setIsOpen;

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setActualOpen(false);
      }
    };

    if (actualOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [actualOpen, setActualOpen]);

  return (
    <div ref={dropdownRef} className="relative inline-block">
      <div onClick={() => setActualOpen(!actualOpen)} className="cursor-pointer">
        {trigger}
      </div>
      {actualOpen && (
        <div
          ref={ref}
          className={cn(
            "absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-card border border-border z-50",
            className
          )}
          {...props}
        >
          <div className="py-1">
            {children}
          </div>
        </div>
      )}
    </div>
  );
});
DropdownMenu.displayName = "DropdownMenu";

const DropdownMenuItem = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      "w-full text-left px-4 py-2 text-sm hover:bg-accent transition-colors",
      className
    )}
    {...props}
  />
));
DropdownMenuItem.displayName = "DropdownMenuItem";

export { DropdownMenu, DropdownMenuItem };
