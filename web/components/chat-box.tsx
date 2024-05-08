"use client";

import useEventSource from "@/hooks/use-event-source";
import { useEffect, useState } from "react";

export default function ChatBox() {
  const { open } = useEventSource(
    "http://127.0.0.1:8000/api/sse/es?prompt=你好"
  );

  useEffect(() => {}, []);
  return (
    <div>
      <input type="text" />
      <button
        onClick={() => {
          open();
        }}
      >
        确认
      </button>
    </div>
  );
}
