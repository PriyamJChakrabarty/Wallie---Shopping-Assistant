"use client"
import React, { useEffect } from 'react'
import Image from "next/image";
import { UserButton } from '@clerk/nextjs';
import { usePathname, useRouter } from 'next/navigation';

function Header() {

    const router=useRouter();
    const onProducts=()=>{
        router.push('/dashboard/products');
   }
   const onCart=()=>{
        router.push('/dashboard/cart');
   }

   const path=usePathname(); 
   useEffect(()=>{
    console.log(path);
   },[path])
  return (
    <div className='flex p-4 items-center justify-between bg-secondary shadow-md'>
        <Image src={'/logo.svg'} width={160} height={50} alt='logo' />
        <ul className='hidden md:flex gap-6'>
            <li className={`hover:text-primary hover:font-bold transition-all cursor-pointer
                ${path=='/dashboard' && 'text-primary font-bold'}
            `}>Dashboard</li>
            <li onClick={onProducts} className={`hover:text-primary hover:font-bold transition-all cursor-pointer
                ${path=='/dashboard/products' && 'text-primary font-bold'}
            `}>Products</li>
            <li onClick={onCart} className={`hover:text-primary hover:font-bold transition-all cursor-pointer
                ${path=='/dashboard/cart' && 'text-primary font-bold'}
            `}>Cart</li>
        </ul>
        <UserButton/>
    </div>
  )
}

export default Header