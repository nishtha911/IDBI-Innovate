import clsx from 'clsx';

export const Card = ({ children, className, ...props }) => {
  return (
    <div 
      className={clsx('bg-white rounded-lg border border-gray-200 shadow-sm', className)} 
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className }) => (
  <div className={clsx('px-6 py-4 border-b border-gray-100 font-semibold text-gray-800', className)}>
    {children}
  </div>
);

export const CardContent = ({ children, className }) => (
  <div className={clsx('p-6', className)}>
    {children}
  </div>
);
