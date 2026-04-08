from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
import traceback
import uuid

from models.reseller_analytics import ResellerAnalytics, BusinessUserAnalytics
from models.reseller import Reseller
from models.busi_user import BusiUser
from models.credit_distribution import CreditDistribution
from models.message_usage import MessageUsageCreditLog
from schemas.reseller_analytics import (
    ResellerDashboardResponse,
    ResellerAnalyticsCreate,
    ResellerAnalyticsUpdate,
    BusinessUserStats,
    Transaction,
    ResellerAnalytics as ResellerAnalyticsSchema
)

from models.message import Message, MessageStatus
from sqlalchemy import extract

logger = logging.getLogger(__name__)

class ResellerAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def generate_reseller_dashboard(self, reseller_id: Any) -> ResellerDashboardResponse:
        """
        Get complete reseller dashboard analytics with flat structure.
        """
        if isinstance(reseller_id, str):
            try:
                reseller_id = uuid.UUID(reseller_id)
            except ValueError:
                pass

        try:
            # 1. Get aggregated analytics from DB (or create headers)
            analytics = self.get_or_create_reseller_analytics(reseller_id)
            
            # 2. Get business user stats
            business_stats_db = self.db.query(BusinessUserAnalytics).filter(
                BusinessUserAnalytics.reseller_id == reseller_id
            ).all()
            
            business_stats = []
            total_messages_sent = 0
            
            for stat in business_stats_db:
                try:
                    msgs = stat.messages_sent or 0
                    total_messages_sent += msgs
                    
                    business_stats.append(BusinessUserStats(
                        user_id=str(stat.business_user_id),
                        business_name=stat.business_name or "Unknown",
                        credits_allocated=stat.credits_allocated or 0,
                        credits_used=stat.credits_used or 0,
                        credits_remaining=stat.credits_remaining or 0,
                        messages_sent=msgs
                    ))
                except Exception as e:
                    logger.error(f"Error parsing business stat {stat.id}: {e}")
                    continue
            
            # 3. Get Real Wallet Balance from Reseller Table
            reseller = self.db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
            wallet_balance = reseller.available_credits if reseller else 0
            total_purchases = reseller.total_credits if reseller else 0
            
            # 4. Get Recent Transactions (Credit Distributions)
            recent_txs_db = self.db.query(CreditDistribution).filter(
                CreditDistribution.from_reseller_id == reseller_id
            ).order_by(desc(CreditDistribution.shared_at)).limit(10).all()
            
            recent_transactions = []
            for tx in recent_txs_db:
                to_business = self.db.query(BusiUser).filter(BusiUser.busi_user_id == tx.to_business_user_id).first()
                b_name = to_business.business_name if to_business else "Unknown"
                
                recent_transactions.append(Transaction(
                    id=str(tx.distribution_id),
                    type="distribution",
                    description=f"Allocated to {b_name}",
                    amount=tx.credits_shared,
                    date=tx.shared_at or datetime.now(timezone.utc),
                    status="completed"
                ))

            # 5. [NEW] Account Info (Real)
            account_info = {
                "user_type": "Reseller", # Or reseller.role if dynamic
                "username": reseller.username if reseller else "Unknown",
                "full_name": reseller.name if reseller else "", # Added full_name
                "email": reseller.email if reseller else "",
                "reseller_id": reseller_id
            }

            # 6. [NEW] Plan Details (Mock)
            plan_details = {
                "plan_type": "MAP 8A",
                "expiry": "UNLIMITED"
            }

            # 7. [NEW] Traffic Source (Real - Aggregated by Country)
            # Aggregate business users by country
            country_stats = {}
            total_businesses = len(business_stats)
            
            # Since 'business_stats' is just a list of Pydantics, we need to query BusiUser for country
            # Optimization: Fetch country in the initial query if possible, but let's just query aggregate now
            
            traffic_db = self.db.query(
                BusiUser.country, 
                func.count(BusiUser.busi_user_id)
            ).filter(
                BusiUser.parent_reseller_id == reseller_id
            ).group_by(BusiUser.country).all()
            
            traffic_source = []
            for country, count in traffic_db:
                label = country if country else "Unknown"
                # Simple color mapping logic or handle on frontend
                traffic_source.append({
                    "name": label,
                    "value": count,
                    "percentage": round((count / max(1, total_businesses)) * 100, 1)
                })
            
            # If empty, add a placeholder or leave empty
            if not traffic_source and total_businesses > 0:
                 traffic_source.append({"name": "Unknown", "value": total_businesses, "percentage": 100})

            # 8. Construct Flat Response
            return ResellerDashboardResponse(
                reseller_id=str(reseller_id),
                total_credits=analytics.total_credits_purchased or 0,
                used_credits=analytics.total_credits_used or 0,
                remaining_credits=analytics.remaining_credits or 0,
                wallet_balance=wallet_balance,
                messages_sent=total_messages_sent,
                business_users=business_stats,
                recent_transactions=recent_transactions,
                plan_details=plan_details,
                account_info=account_info,
                traffic_source=traffic_source,
                graph_data=self.get_reseller_graph_data(reseller_id),
                last_updated=analytics.updated_at or datetime.now(timezone.utc)
            )
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in generate_reseller_dashboard: {e}")
            raise e

    def get_reseller_graph_data(self, reseller_id: Any) -> List[dict]:
        """
        [AGGREGATE GRAPH] Aggregates all messages from all business users 
        belonging to this reseller, grouped by month for the current year.
        Source: MessageUsageCreditLog for highest accuracy.
        """
        current_year = datetime.now().year
        
        try:
            # Query MessageUsageCreditLog joined with BusiUser to filter by reseller
            stats = self.db.query(
                extract('month', MessageUsageCreditLog.timestamp).label('month'),
                func.count(MessageUsageCreditLog.usage_id).label('total')
            ).join(
                BusiUser, BusiUser.busi_user_id == MessageUsageCreditLog.busi_user_id
            ).filter(
                BusiUser.parent_reseller_id == reseller_id,
                extract('year', MessageUsageCreditLog.timestamp) == current_year
            ).group_by('month').order_by('month').all()
            
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            result = []
            stats_dict = {int(s.month): s for s in stats}
            
            for i in range(1, 13):
                month_stat = stats_dict.get(i)
                result.append({
                    "name": month_names[i-1],
                    "sent": month_stat.total if month_stat else 0,
                    "delivered": 0 # User requested to remove delivery line, keeping key for contract compatibility
                })
            return result
        except Exception as e:
            logger.error(f"Error in get_reseller_graph_data: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in get_reseller_graph_data: {e}")
            return []

    def get_or_create_reseller_analytics(self, reseller_id: Any) -> ResellerAnalytics:
        """Get existing analytics or create new one for reseller."""
        if isinstance(reseller_id, str):
            try:
                reseller_id = uuid.UUID(reseller_id)
            except ValueError:
                pass
        try:
            analytics = self.db.query(ResellerAnalytics).filter(
                ResellerAnalytics.reseller_id == reseller_id
            ).first()
            
            if not analytics:
                reseller_exists = self.db.query(Reseller.reseller_id).filter(Reseller.reseller_id == reseller_id).scalar()
                
                if not reseller_exists:
                    logger.warning(f"Reseller {reseller_id} not found when creating analytics.")
                    # Return safe dummy
                    return ResellerAnalytics(
                        reseller_id=reseller_id, 
                        total_credits_purchased=0,
                        total_credits_distributed=0,
                        total_credits_used=0,
                        remaining_credits=0,
                        business_user_stats=[],
                        updated_at=datetime.now(timezone.utc)
                    )

                analytics = ResellerAnalytics(
                    reseller_id=reseller_id,
                    total_credits_purchased=0,
                    total_credits_distributed=0,
                    total_credits_used=0,
                    remaining_credits=0,
                    business_user_stats=[],
                    updated_at=datetime.now(timezone.utc)
                )
                self.db.add(analytics)
                self.db.commit()
                self.db.refresh(analytics)
                self._update_reseller_aggregates(analytics)
            
            return analytics
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in get_or_create_reseller_analytics: {e}")
            # Fallback
            return ResellerAnalytics(
                reseller_id=reseller_id,
                total_credits_purchased=0,
                total_credits_distributed=0,
                total_credits_used=0,
                remaining_credits=0,
                business_user_stats=[],
                updated_at=datetime.now(timezone.utc)
            )

    def regenerate_all_analytics(self, reseller_id: Any) -> ResellerDashboardResponse:
        """Force recalculate ALL analytics."""
        if isinstance(reseller_id, str):
            try:
                reseller_id = uuid.UUID(reseller_id)
            except ValueError:
                pass
        logger.info(f"Regenerating analytics for reseller {reseller_id}")
        
        try:
            businesses = self.db.query(BusiUser).filter(
                BusiUser.parent_reseller_id == reseller_id
            ).all()
            
            for business in businesses:
                self.recalculate_business_analytics(str(business.busi_user_id), str(reseller_id))
                
            analytics = self.get_or_create_reseller_analytics(reseller_id)
            if analytics.id is not None:
                self._update_reseller_aggregates(analytics)
            
            return self.generate_reseller_dashboard(reseller_id)
        except Exception as e:
            logger.error(f"Error regenerating analytics: {e}")
            raise e

    def recalculate_business_analytics(self, business_user_id: str, reseller_id: str) -> Optional[BusinessUserAnalytics]:
        try:
            analytics = self.db.query(BusinessUserAnalytics).filter(
                BusinessUserAnalytics.business_user_id == business_user_id
            ).first()

            business_user = self.db.query(BusiUser).filter(BusiUser.busi_user_id == business_user_id).first()
            if not business_user:
                return None

            business_name = getattr(business_user, 'business_name', 'Unknown Business')

            if not analytics:
                analytics = BusinessUserAnalytics(
                    reseller_id=reseller_id,
                    business_user_id=business_user_id,
                    business_name=business_name
                )
                self.db.add(analytics)
            
            # FIXED COLUMNS: credits_shared, busi_user_id
            credits_allocated = self.db.query(func.sum(CreditDistribution.credits_shared)).filter(
                CreditDistribution.from_reseller_id == reseller_id,
                CreditDistribution.to_business_user_id == business_user_id
            ).scalar() or 0
            
            credits_used = self.db.query(func.sum(MessageUsageCreditLog.credits_deducted)).filter(
                MessageUsageCreditLog.busi_user_id == business_user_id,
                MessageUsageCreditLog.credits_deducted > 0  # Only sum positive values (actual deductions)
            ).scalar() or 0
            
            messages_sent = self.db.query(MessageUsageCreditLog).filter(
                MessageUsageCreditLog.busi_user_id == business_user_id
            ).count()
            
            credits_remaining = max(0, credits_allocated - credits_used)
            
            analytics.business_name = business_name 
            analytics.credits_allocated = credits_allocated
            analytics.credits_used = credits_used
            analytics.credits_remaining = credits_remaining
            analytics.messages_sent = messages_sent
            analytics.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(analytics)
            return analytics
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recalculating business analytics: {e}")
            return None

    def _update_reseller_aggregates(self, analytics: ResellerAnalytics) -> ResellerAnalytics:
        try:
            reseller_id = str(analytics.reseller_id)
            
            aggregates = self.db.query(
                func.sum(BusinessUserAnalytics.credits_allocated).label('total_distributed'),
                func.sum(BusinessUserAnalytics.credits_used).label('total_used')
            ).filter(
                BusinessUserAnalytics.reseller_id == reseller_id
            ).first()
            
            total_distributed = aggregates.total_distributed or 0
            total_used = aggregates.total_used or 0
            
            reseller = self.db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
            total_credits_purchased = reseller.total_credits if reseller else 0
            
            # Logic: Remaining = Purchased - Distributed 
            # (Assuming distributed credits are deducted from reseller's main pool)
            remaining_credits = max(0, total_credits_purchased - total_distributed)
            
            analytics.total_credits_purchased = total_credits_purchased
            analytics.total_credits_distributed = total_distributed
            analytics.total_credits_used = total_used
            analytics.remaining_credits = remaining_credits
            analytics.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(analytics)
            return analytics
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating reseller aggregates: {e}")
            raise e
