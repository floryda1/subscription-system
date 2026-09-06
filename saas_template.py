"""
MICRO SAAS
"""


# some things to fix
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class BillingType(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class CustomerType(Enum):
    PERSONAL = "personal"
    BUSINESS = "business"

class PlanType(Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class NotificationType(Enum):
    SMS = "sms"
    EMAIL = "email"

# plan

@dataclass
class Plan:
    name: PlanType
    monthly_price: float

    def __str__(self):
        return f"plan: {self.name.value}: {self.monthly_price} PLN."

# subscription choice

basic = Plan(PlanType.BASIC, 0)
pro = Plan(PlanType.PRO, 100)
enterprise = Plan(PlanType.ENTERPRISE, 350)

def plan_factory(plan_name: PlanType) -> Plan:
    if plan_name == PlanType.BASIC:
        return basic
    elif plan_name == PlanType.PRO:
        return pro
    elif plan_name == PlanType.ENTERPRISE:
        return enterprise
    else:
        raise ValueError(f"Unknown plan: {plan_name}")

# DISCOUNT

class Discount(ABC):
    @abstractmethod
    def calculate_discount(
            self,
            plan: Plan,
            billing_type,
            customer_type,
            team_size
    ):
        pass

class YearlyDiscount(Discount):
    def calculate_discount(
            self,
            plan: Plan,
            billing_type,
            customer_type,
            team_size
    ):
            return plan.monthly_price * 0.9

class LargeTeamDiscount(Discount):
    def calculate_discount(
            self,
            plan: Plan,
            billing_type,
            customer_type,
            team_size
    ):

        return  plan.monthly_price * 0.8


class NoDiscount(Discount):
    def calculate_discount(
        self,
        plan: Plan,
        billing_type: BillingType,
        customer_type: CustomerType,
        team_size: int
    ):
        return plan.monthly_price

class CalculateFinalDiscount:
    @staticmethod
    def get_discount(
        plan: Plan,
        billing_type: BillingType,
        customer_type: CustomerType,
        team_size: int
    ) -> Discount:

        if plan.name == PlanType.PRO and billing_type == BillingType.YEARLY:
            return YearlyDiscount()

        if customer_type == CustomerType.BUSINESS and team_size >= 10:
            return LargeTeamDiscount()

        return NoDiscount()

# FINAL PRICE


def calculate_final_price(
    plan: Plan,
    billing_type: BillingType,
    customer_type: CustomerType,
    team_size: int = 1
) -> float:

    months = 12 if billing_type == BillingType.YEARLY else 1

    discount = CalculateFinalDiscount.get_discount(
        plan=plan,
        billing_type=billing_type,
        customer_type=customer_type,
        team_size=team_size
    )

    discounted_monthly_price = discount.calculate_discount(
        plan=plan,
        billing_type=billing_type,
        customer_type=customer_type,
        team_size=team_size
    )

    return round(discounted_monthly_price * months, 2)

# NOTIFICATION FACTORY

class NotificationSender(ABC):
    @abstractmethod
    def send(self, recipient: str, message:str ) -> None:
        pass

class EmailNotificationSender(NotificationSender):
    def send(self, recipient: str, message:str) -> None:
        print(f"Sending email to {recipient}: {message}")

class SMSNotificationSender(NotificationSender):
    def send(self, recipient: str, message:str) -> None:
        print(f"Sending SMS to {recipient}: {message}")

#NOTIFICATION SENDER

class NotificationService:
    def __init__(self, sender: NotificationSender):
        self.sender = sender

    def notify_renewal(self, recipient: str, plan_name: PlanType, price: float) -> None:
        message = f"the {plan_name} plan was reneved. price: {price} PLN."
        self.sender.send(recipient, message)

    def notify_cancellation(self, recipient: str, plan_name: PlanType) -> None:
        message = f"cancelled plan: {plan_name}."
        self.sender.send(recipient, message)

class ActiveSubscription:
    def __init__(self, user_email: str,
        plan_name: PlanType,
        final_price: float,
        billing_type: BillingType):

        self.user_email = user_email
        self.plan_name = plan_name
        self.final_price = final_price
        self.billing_type = billing_type
    def monthly_revenue(self):
        if self.billing_type == BillingType.YEARLY:
            return self.final_price / 12
        return self.final_price

class SubscriptionRepository:
    def __init__(self):
        self._subscriptions = []
    def add(self, subscription: ActiveSubscription) -> None:
        self._subscriptions.append(subscription)
    def get_all_active(self) -> list:
        return self._subscriptions

# REVENUE CALCULATOR

class MRRCalculator:
    def calculate_mrr(self, active_subscriptions: list):
        for sub in active_subscriptions:
            yield sub.monthly_revenue()

def main():
    # 1. klient wybiera plan
    plan = plan_factory(PlanType.PRO)

    # 2. liczysz finalną cenę (docelowo przez DiscountStrategy, nie if/elif)
    final_price = calculate_final_price(plan, billing_type=BillingType.YEARLY,
    customer_type=CustomerType.BUSINESS, team_size=12)

    # 3. tworzysz obiekt reprezentujący aktywną subskrypcję tego klienta
    subscription = ActiveSubscription(
        user_email="klient@example.com",
        plan_name=plan.name,
        final_price=final_price,
        billing_type=BillingType.YEARLY
    )

    # 4. zapisujesz do repozytorium (tu dodałbyś więcej klientów w pętli/kolejnych wywołaniach)
    repo = SubscriptionRepository()
    repo.add(subscription)

    # 5. powiadamiasz klienta - PRZEZ KAŻDY skonfigurowany kanał naraz
    channels = [NotificationService(EmailNotificationSender()), NotificationService(SMSNotificationSender())]
    for service in channels:
        service.notify_renewal(subscription.user_email, subscription.plan_name, subscription.final_price)

    # 6. na koniec liczysz MRR całej firmy z repozytorium
    calculator = MRRCalculator()

    mrr = sum(calculator.calculate_mrr(repo.get_all_active()))

    print(mrr)

if __name__ == "__main__":
    main()
#test comment for branch