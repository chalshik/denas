"use client";

import React from "react";
import { useRouter } from "next/navigation";
import {
  Navbar as HeroNavbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  NavbarMenu,
  NavbarMenuToggle,
  NavbarMenuItem,
} from "@heroui/navbar";
import { Button } from "@heroui/button";
import { Link } from "@heroui/link";

import { siteConfig } from "@/config/site";
import { useAuth } from "@/contexts/AuthContext";

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const { user, signOut, loading } = useAuth();
  const router = useRouter();

  const menuItems = [
    { name: "Home", href: "/" },
    { name: "Products", href: "/shop" },
    { name: "About", href: "/about" },
  ];

  const isAdmin = user?.role === "admin";

  return (
    <HeroNavbar
      className="bg-background/60 backdrop-blur-md"
      onMenuOpenChange={setIsMenuOpen}
    >
      <NavbarContent>
        <NavbarMenuToggle
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          className="sm:hidden"
        />
        <NavbarBrand>
          <Link className="font-bold text-inherit" href="/">
            {siteConfig.name}
          </Link>
        </NavbarBrand>
      </NavbarContent>

      <NavbarContent className="hidden sm:flex gap-4" justify="center">
        {menuItems.map((item) => (
          <NavbarItem key={item.name}>
            <Link className="w-full" color="foreground" href={item.href}>
              {item.name}
            </Link>
          </NavbarItem>
        ))}
      </NavbarContent>

      <NavbarContent justify="end">
        {!loading && user ? (
          <>
            <NavbarItem className="hidden sm:flex">
              <span className="text-sm text-gray-600">{user.phone}</span>
            </NavbarItem>
            {isAdmin && (
              <NavbarItem>
                <Button
                  as={Link}
                  color="secondary"
                  href="/admin/products"
                  variant="flat"
                >
                  Admin Panel
                </Button>
              </NavbarItem>
            )}
            <NavbarItem>
              <Button
                color="danger"
                variant="bordered"
                onPress={async () => {
                  await signOut();
                  router.push("/");
                }}
              >
                Sign Out
              </Button>
            </NavbarItem>
          </>
        ) : !loading ? (
          <>
            <NavbarItem className="hidden sm:flex">
              <Button
                as={Link}
                color="primary"
                href="/auth/login"
                variant="flat"
              >
                Sign In
              </Button>
            </NavbarItem>
            <NavbarItem>
              <Button
                as={Link}
                color="primary"
                href="/auth/register"
                variant="bordered"
              >
                Sign Up
              </Button>
            </NavbarItem>
          </>
        ) : null}
      </NavbarContent>

      <NavbarMenu>
        {menuItems.map((item, index) => (
          <NavbarMenuItem key={`${item.name}-${index}`}>
            <Link
              className="w-full"
              color="foreground"
              href={item.href}
              size="lg"
            >
              {item.name}
            </Link>
          </NavbarMenuItem>
        ))}
        {!loading && user ? (
          <>
            <NavbarMenuItem>
              <div className="p-4 text-sm text-gray-600">
                Logged in as: {user.phone}
              </div>
            </NavbarMenuItem>
            {isAdmin && (
              <NavbarMenuItem>
                <Button
                  as={Link}
                  className="w-full"
                  color="secondary"
                  href="/admin/products"
                  variant="flat"
                >
                  Admin Panel
                </Button>
              </NavbarMenuItem>
            )}
            <NavbarMenuItem>
              <Button
                className="w-full"
                color="danger"
                variant="bordered"
                onPress={async () => {
                  await signOut();
                  router.push("/");
                }}
              >
                Sign Out
              </Button>
            </NavbarMenuItem>
          </>
        ) : !loading ? (
          <>
            <NavbarMenuItem>
              <Button
                as={Link}
                className="w-full"
                color="primary"
                href="/auth/login"
                variant="flat"
              >
                Sign In
              </Button>
            </NavbarMenuItem>
            <NavbarMenuItem>
              <Button
                as={Link}
                className="w-full"
                color="primary"
                href="/auth/register"
                variant="bordered"
              >
                Sign Up
              </Button>
            </NavbarMenuItem>
          </>
        ) : null}
      </NavbarMenu>
    </HeroNavbar>
  );
}
