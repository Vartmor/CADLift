import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';

interface PageTransitionProps {
    children: React.ReactNode;
}

/**
 * Subtle page transition - smooth fade with gentle slide.
 * Light on the eyes, clean and professional.
 */
const PageTransition: React.FC<PageTransitionProps> = ({ children }) => {
    const location = useLocation();
    const [displayChildren, setDisplayChildren] = useState(children);
    const [transitionClass, setTransitionClass] = useState('');
    const prevPathRef = useRef(location.pathname);

    useEffect(() => {
        if (location.pathname !== prevPathRef.current) {
            prevPathRef.current = location.pathname;

            // Quick fade out
            setTransitionClass('page-fade-out');

            // Swap content after fade out
            setTimeout(() => {
                setDisplayChildren(children);
                setTransitionClass('page-fade-in');

                // Remove animation class after complete
                setTimeout(() => {
                    setTransitionClass('');
                }, 300);
            }, 150);
        } else {
            setDisplayChildren(children);
        }
    }, [location.pathname, children]);

    return (
        <div className={`page-transition ${transitionClass}`}>
            {displayChildren}
        </div>
    );
};

export default PageTransition;
