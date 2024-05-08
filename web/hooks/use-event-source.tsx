import { useRef, useState } from "react";

type useEventSourceOpts = {
  onEnd?: () => void;
  map?: {
    messsage?: string;
    end?: string;
  };
  print?: boolean;
  parse?: boolean;
} & EventSourceInit;

export default function useEventSource<Data>(
  url: string,
  opts?: useEventSourceOpts
) {
  const refES = useRef<EventSource>();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Data[]>([]);

  const { print = true } = opts ?? {};

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
        const data = opts?.parse ? JSON.parse(event.data) : event.data;
        print && console.log(data);
        setData((prev) => [...prev, data]);
      }
    );

    refES.current.addEventListener(opts?.map?.end ?? "end", (event) => {
      opts?.onEnd?.();
      close();
    });

    refES.current.onerror = (event) => {
      close();
    };
  }

  function close() {
    refES.current?.close();
    setLoading(false);
  }

  return { open, close, data, loading };
}
