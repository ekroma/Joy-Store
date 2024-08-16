import React, { useState } from 'react'
import { FaShoppingCart, FaTachometerAlt, FaUsers } from 'react-icons/fa'
import { Link } from 'react-router-dom'
import logo from '../../assets/react.svg'
import SidebarItem from '../SidebarItems/SidebarItems'
import './Sidebar.scss'

const Sidebar: React.FC = () => {
	const [openList, setOpenList] = useState<string | null>(null)

	const toggleList =
		(listName: string) => (e: React.MouseEvent<HTMLAnchorElement>) => {
			e.preventDefault()
			setOpenList(openList === listName ? null : listName)
		}

	const items = [
		{
			links: '/dashboard',
			listName: 'dashboard',
			title: 'Dashboard',
			children: [
				{ label: 'Analytics', link: '/analytics' },
				{ label: 'Sales', link: '/sales' },
			],
			icon: <FaTachometerAlt />,
		},
		{
			links: '/users',
			listName: 'users',
			title: 'Users',
			children: [
				{ label: 'User Management', link: '/users/user-management' },
				{ label: 'My Profile', link: '/users/my-profile' },
			],
			icon: <FaUsers />,
		},
		{
			links: '/e-commerce',
			listName: 'e-commerce',
			title: 'E-commerce',
			children: [
				{ label: 'Product Management', link: '/e-commerce/product-management' },
				{ label: 'Product Grid', link: '/e-commerce/product-grid' },
			],
			icon: <FaShoppingCart />,
		},
	]

	return (
		<div>
			<aside>
				<nav className='sidebar'>
					<img src={logo} alt='logo' className='sidebar_logo' />
					<Link className='sidebar_h1' to='/'>Online store pro</Link>
					<h2 className='sidebar_h2'>APP</h2>
					<ul className='sidebar_text'>
						{items.map((item, index) => (
							<SidebarItem
								key={index}
								links={item.links}
								listName={item.listName}
								title={item.title}
								children={item.children}
								isOpen={openList === item.listName}
								toggleList={toggleList}
								icon={item.icon}
							/>
						))}
					</ul>
					<span className='sidebar_span'>
						<p>© 2021 ONLINE STORE PRO</p>
					</span>
				</nav>
			</aside>
		</div>
	)
}

export default Sidebar
