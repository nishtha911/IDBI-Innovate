import { Card, CardContent } from './Card';
import clsx from 'clsx';

export const MetricCard = ({ title, value, icon: Icon, trend, trendLabel, colorClass = "text-finsight-teal" }) => {
  return (
    <Card>
      <CardContent className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-gray-800">{value}</h3>
          
          {trend && (
            <div className="mt-4 flex items-center gap-2">
              <span className={clsx(
                "text-xs font-medium px-2 py-1 rounded-full",
                trend === 'up' ? "bg-green-100 text-green-700" : 
                trend === 'down' ? "bg-red-100 text-red-700" : 
                "bg-gray-100 text-gray-700"
              )}>
                {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '-'} 
                {trendLabel && ` ${trendLabel}`}
              </span>
            </div>
          )}
        </div>
        <div className={clsx("p-3 rounded-lg bg-gray-50", colorClass)}>
          <Icon size={24} />
        </div>
      </CardContent>
    </Card>
  );
};
