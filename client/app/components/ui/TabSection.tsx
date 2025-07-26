"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TabSection() {
  const pathname = usePathname();

  const tabs = [
    { name: "Project", href: "/project" },
    { name: "Voices", href: "/project/voices" },
  ];

  return (
    <div role="tablist" className="tabs tabs-lift">
      {tabs.map((tab) => {
        const isActive = pathname === tab.href;
        return (
          <Link
            key={tab.name}
            href={tab.href}
            className={`tab ${isActive && "tab-active"}`}
          >
            {tab.name}
          </Link>
        );
      })}
    </div>
  );
}
