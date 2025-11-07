import React from 'react';

interface LogoProps {
  size?: 'small' | 'medium' | 'large' | 'default';
  className?: string;
  alt?: string;
}

const Logo: React.FC<LogoProps> = ({ 
  size = 'default', 
  className = '', 
  alt = 'CapeControl Logo' 
}) => {
  // Select appropriate image size based on the size prop
  const getImageSrc = () => {
    switch (size) {
      case 'small':
        return '/icons/logo-64x64.png';
      case 'medium':
        return '/icons/logo-128x128.png';
      case 'large':
        return '/icons/logo-256x256.png';
      default:
        return '/LogoW.png'; // Use original for default
    }
  };

  const sizeClassName = size !== 'default' ? `cc-logo--${size}` : '';
  const combinedClassName = `cc-logo ${sizeClassName} ${className}`.trim();

  return (
    <img 
      src={getImageSrc()} 
      alt={alt} 
      className={combinedClassName}
    />
  );
};

export default Logo;