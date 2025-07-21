"use client";

import React from "react";
import { Button } from "@heroui/button";
import { Navbar, NavbarBrand, NavbarContent, NavbarItem } from "@heroui/navbar";
import { useRouter, usePathname } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = async () => {
    try {
      await signOut();
      router.push("/");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const navItems = [
    { label: "Catalog", path: "/client/catalog", icon: "🛍️" },
    { label: "Favorites", path: "/client/favorites", icon: "❤️" },
    { label: "Cart", path: "/client/cart", icon: "🛒" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Header */}
      <Navbar className="bg-white shadow-sm border-b" maxWidth="full">
        <NavbarBrand>
          <h1 className="text-2xl font-bold text-gray-900">Denas</h1>
        </NavbarBrand>

        <NavbarContent className="hidden sm:flex gap-4" justify="center">
          {navItems.map((item) => (
            <NavbarItem key={item.path}>
              <Button
                color={pathname === item.path ? "primary" : "default"}
                startContent={<span>{item.icon}</span>}
                variant={pathname === item.path ? "solid" : "light"}
                onPress={() => router.push(item.path)}
              >
                {item.label}
              </Button>
            </NavbarItem>
          ))}
        </NavbarContent>

        <NavbarContent justify="end">
          <NavbarItem className="flex items-center gap-2">
            <span className="text-gray-600 text-sm">{user?.phone}</span>
            <Button size="sm" variant="bordered" onPress={handleLogout}>
              Logout
            </Button>
          </NavbarItem>
        </NavbarContent>
      </Navbar>

      {/* Mobile Navigation */}
      <div className="sm:hidden bg-white border-b shadow-sm">
        <div className="flex justify-around py-2">
          {navItems.map((item) => (
            <Button
              key={item.path}
              className="flex-col h-12 min-w-0"
              color={pathname === item.path ? "primary" : "default"}
              size="sm"
              variant={pathname === item.path ? "solid" : "light"}
              onPress={() => router.push(item.path)}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="text-xs">{item.label}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">{children}</main>
    </div>
  );
}
