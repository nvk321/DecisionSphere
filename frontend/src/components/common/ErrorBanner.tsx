import * as React from "react";
import { cn, copyToClipboard } from "@/lib/utils";
import { AlertCircle, Copy, Check, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface ErrorBannerProps {
  title?: string;
  message: string;
  code?: string;
  requestId?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorBanner({
  title = "Error Encountered",
  message,
  code,
  requestId,
  onRetry,
  className,
}: ErrorBannerProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopyRequestId = async () => {
    if (requestId) {
      const success = await copyToClipboard(requestId);
      if (success) {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    }
  };

  return (
    <div
      role="alert"
      className={cn(
        "rounded-lg border border-rose-800/60 bg-rose-950/40 p-4 text-rose-200 shadow-sm",
        className
      )}
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-semibold text-sm text-rose-100">{title}</h4>
            {code && (
              <span className="rounded bg-rose-900/60 px-1.5 py-0.5 text-[10px] font-mono font-bold text-rose-300 border border-rose-700/50">
                {code}
              </span>
            )}
          </div>
          <p className="text-xs text-rose-200/90 leading-relaxed">{message}</p>

          {requestId && (
            <div className="flex items-center gap-2 pt-1 text-[11px] text-rose-300/80">
              <span className="font-mono">Correlation ID: {requestId}</span>
              <button
                type="button"
                onClick={handleCopyRequestId}
                className="hover:text-rose-100 transition-colors p-0.5 rounded cursor-pointer"
                title="Copy Request ID"
                aria-label="Copy Request ID"
              >
                {copied ? (
                  <Check className="h-3 w-3 text-emerald-400" />
                ) : (
                  <Copy className="h-3 w-3" />
                )}
              </button>
            </div>
          )}
        </div>

        {onRetry && (
          <Button
            size="sm"
            variant="outline"
            onClick={onRetry}
            className="border-rose-700/60 text-rose-200 hover:bg-rose-900/40 text-xs shrink-0"
          >
            <RefreshCw className="h-3 w-3 mr-1.5" />
            Retry
          </Button>
        )}
      </div>
    </div>
  );
}
