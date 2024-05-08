import { useRef, useState } from "react";

type useEventSourceOpts = {
  onEnd?: () => void;
  map?: Record<"messsage" | "end", string>;
} & EventSourceInit;

export default function useEventSource(url: string, opts?: useEventSourceOpts) {
  const refES = useRef<EventSource>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error>();
  const [data, setData] = useState<any[]>([]);

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

    if (!opts?.map?.messsage || opts?.map?.messsage === "message") {
      refES.current.onmessage = (event) => {
        setData((prev) => [...prev, event.data]);
      };
    } else {
      refES.current.addEventListener(opts.map.messsage, (event) => {
        setData((prev) => [...prev, event.data]);
      });
    }

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
