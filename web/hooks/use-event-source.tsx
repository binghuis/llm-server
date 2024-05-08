import { useRef, useState } from "react";

type useEventSourceOpts = {
  onEnd?: () => void;
  map?: Record<"messsage" | "end", string>;
  formater?: (data: any) => any;
} & EventSourceInit;

export default function useEventSource<Data>(
  url: string,
  opts?: useEventSourceOpts
) {
  const refES = useRef<EventSource>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error>();
  const [data, setData] = useState<Data[]>([]);

  function open() {
    if (refES.current) {
      close();
    }

    refES.current = new EventSource(url, {
      withCredentials: opts?.withCredentials,
    });

    refES.current.onopen = (event) => {
      setData([]);
      setLoading(true);
    };

    refES.current.addEventListener(
      opts?.map?.messsage ?? "message",
      (event) => {
        setData((prev) => [
          ...prev,
          opts?.formater ? opts.formater(event.data) : event.data,
        ]);
      }
    );

    refES.current.addEventListener(opts?.map?.end ?? "end", (event) => {
      opts?.onEnd?.();
      setLoading(false);
    });

    refES.current.onerror = (event) => {
      setLoading(false);
      setError(new Error(event.type));
    };
  }

  function close() {
    refES.current?.close();
    setLoading(false);
  }

  return { open, close, data, loading, error };
}
