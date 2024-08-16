import React from 'react'
import { FaChevronDown, FaChevronUp } from 'react-icons/fa'
import { Link } from 'react-router-dom'

interface ChildItem {
	label: string
	link: string
}

interface SidebarItemProps {
	listName: string
	title: string
	children: ChildItem[]
	links: string
	isOpen: boolean
	toggleList: (
		listName: string
	) => (e: React.MouseEvent<HTMLAnchorElement>) => void
	icon: React.ReactNode
}

const SidebarItem: React.FC<SidebarItemProps> = ({
	listName,
	title,
	children,
	isOpen,
	toggleList,
	links,
	icon,
}) => {
	return (
		<div>
			<li>
				<Link
					to={links}
					className={`button_neon ${isOpen ? 'active' : ''}`}
					onClick={toggleList(listName)}
					aria-expanded={isOpen}
				>
					<span className='sidebar_svg'>{icon}</span>
					{title}
					<span className='arrow_icon'>
						{isOpen ? <FaChevronUp /> : <FaChevronDown />}
					</span>
				</Link>
				{isOpen && (
					<div className='button_background'>
						<ul>
							{children.map((child, index) => (
								<li key={index} className='button_down'>
									<Link to={child.link}>{child.label}</Link>
								</li>
							))}
						</ul>
					</div>
				)}
			</li>
		</div>
	)
}

export default SidebarItem
