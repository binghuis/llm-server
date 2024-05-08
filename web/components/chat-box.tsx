"use client";

import useEventSource from "@/hooks/use-event-source";

export default function ChatBox() {
  const { open, data } = useEventSource(
    "http://127.0.0.1:8000/api/sse/es?prompt=你好",
    {
      map: {
        messsage: "add",
      },
      parse: true,
    }
  );

  return (
    <div>
      {data.join("")}
      <button
        onClick={() => {
          open();
        }}
      >
        嗨！
      </button>
    </div>
  );
}
