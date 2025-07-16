'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Navbar as HeroNavbar, NavbarBrand, NavbarContent, NavbarItem, NavbarMenu, NavbarMenuToggle, NavbarMenuItem } from '@heroui/navbar';
import { Button } from '@heroui/button';
import { Link } from '@heroui/link';
import { siteConfig } from '@/config/site';
import { useAuth } from '@/hooks/useAuth';

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const { user, isAdmin, logout } = useAuth();
  const router = useRouter();

  const menuItems = [
    { name: "Home", href: "/" },
    { name: "Products", href: "/shop" },
    { name: "About", href: "/about" },
  ];

  return (
    <HeroNavbar onMenuOpenChange={setIsMenuOpen} className="bg-background/60 backdrop-blur-md">
      <NavbarContent>
        <NavbarMenuToggle
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          className="sm:hidden"
        />
        <NavbarBrand>
          <Link href="/" className="font-bold text-inherit">
            {siteConfig.name}
          </Link>
        </NavbarBrand>
      </NavbarContent>

      <NavbarContent className="hidden sm:flex gap-4" justify="center">
        {menuItems.map((item) => (
          <NavbarItem key={item.name}>
            <Link
              color="foreground"
              href={item.href}
              className="w-full"
            >
              {item.name}
            </Link>
          </NavbarItem>
        ))}
      </NavbarContent>

      <NavbarContent justify="end">
        {user ? (
          <>
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
                  await logout();
                  router.push('/');
                }}
              >
                Sign Out
              </Button>
            </NavbarItem>
          </>
        ) : (
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
        )}
      </NavbarContent>

      <NavbarMenu>
        {menuItems.map((item, index) => (
          <NavbarMenuItem key={`${item.name}-${index}`}>
            <Link
              color="foreground"
              href={item.href}
              size="lg"
              className="w-full"
            >
              {item.name}
            </Link>
          </NavbarMenuItem>
        ))}
        {user ? (
          <>
            {isAdmin && (
              <NavbarMenuItem>
                <Button
                  as={Link}
                  color="secondary"
                  href="/admin/products"
                  variant="flat"
                  className="w-full"
                >
                  Admin Panel
                </Button>
              </NavbarMenuItem>
            )}
            <NavbarMenuItem>
              <Button
                color="danger"
                variant="bordered"
                className="w-full"
                onPress={async () => {
                  await logout();
                  router.push('/');
                }}
              >
                Sign Out
              </Button>
            </NavbarMenuItem>
          </>
        ) : (
          <>
            <NavbarMenuItem>
              <Button
                as={Link}
                color="primary"
                href="/auth/login"
                variant="flat"
                className="w-full"
              >
                Sign In
              </Button>
            </NavbarMenuItem>
            <NavbarMenuItem>
              <Button
                as={Link}
                color="primary"
                href="/auth/register"
                variant="bordered"
                className="w-full"
              >
                Sign Up
              </Button>
            </NavbarMenuItem>
          </>
        )}
      </NavbarMenu>
    </HeroNavbar>
  );
} 