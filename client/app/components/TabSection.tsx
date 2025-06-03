"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TabSection() {
  const pathname = usePathname();

  const tabs = [
    { name: "Project", href: "/project" },
    { name: "Voices", href: "/voices" },
  ];

  return (
    <div className="flex gap-1 border-b border-gray-200 mb-4">
      {tabs.map((tab) => {
        const isActive = pathname === tab.href;
        return (
          <Link
            key={tab.name}
            href={tab.href}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              isActive
                ? "bg-blue-100 text-blue-700 border-b-2 border-blue-700"
                : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
            }`}
          >
            {tab.name}
          </Link>
        );
      })}
    </div>
  );
}
