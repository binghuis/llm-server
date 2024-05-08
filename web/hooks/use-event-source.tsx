import { useRef, useState } from "react";

type useEventSourceOpts = {
  onFinished?: () => void;
} & EventSourceInit;

export default function useEventSource(url: string, opts?: useEventSourceOpts) {
  const refES = useRef<EventSource>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error>();

  function open() {
    if (refES.current) {
      refES.current.close();
    }
    refES.current = new EventSource(url, {
      withCredentials: opts?.withCredentials,
    });
    refES.current.onopen = (event) => {
      setLoading(true);
    };

    refES.current.onmessage = (event) => {
      console.log(event);
    };

    refES.current.onerror = (event) => {
      setLoading(false);
      setError(new Error(event.type));
      console.log("error", event);
    };

    refES.current.addEventListener("end", (event) => {
      opts?.onFinished?.();
      close();
    });

    refES.current.addEventListener("add", (event) => {
      console.log("add", JSON.parse(event.data));
    });
  }

  function close() {
    refES.current?.close();
    setLoading(false);
  }

  return { open, close, loading, error };
}
