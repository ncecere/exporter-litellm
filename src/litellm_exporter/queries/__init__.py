class MetricQueries:
    @staticmethod
    def get_spend_metrics(time_window: str) -> str:
        return """
        WITH spend_data AS (
            SELECT
                s.model,
                SUM(s.spend) as total_spend,
                SUM(s.total_tokens) as total_tokens,
                SUM(s.prompt_tokens) as prompt_tokens,
                SUM(s.completion_tokens) as completion_tokens,
                COUNT(*) as request_count,
                COUNT(CASE WHEN s.cache_hit = 'true' THEN 1 END) as cache_hits,
                COUNT(CASE WHEN s.cache_hit = 'false' THEN 1 END) as cache_misses,
                u.user_id,
                u.user_alias,
                t.team_id,
                t.team_alias,
                o.organization_id,
                o.organization_alias
            FROM "LiteLLM_SpendLogs" s
            LEFT JOIN "LiteLLM_UserTable" u ON s."user" = u.user_id
            LEFT JOIN "LiteLLM_TeamTable" t ON s.team_id = t.team_id
            LEFT JOIN "LiteLLM_OrganizationTable" o ON t.organization_id = o.organization_id
            WHERE s."startTime" >= NOW() - INTERVAL %(time_window)s
            GROUP BY s.model, u.user_id, u.user_alias, t.team_id, t.team_alias,
                     o.organization_id, o.organization_alias
        )
        SELECT * FROM spend_data
        """

    @staticmethod
    def get_rate_limits() -> str:
        return """
        -- Get user rate limits and blocked status
        SELECT
            'user' as entity_type,
            u.user_id as entity_id,
            u.user_alias as entity_alias,
            u.tpm_limit,
            u.rpm_limit,
            u.max_parallel_requests,
            CASE
                WHEN e.blocked = true THEN true
                ELSE false
            END as is_blocked
        FROM "LiteLLM_UserTable" u
        LEFT JOIN "LiteLLM_EndUserTable" e ON u.user_id = e.user_id
        WHERE u.tpm_limit IS NOT NULL
           OR u.rpm_limit IS NOT NULL
           OR u.max_parallel_requests IS NOT NULL
           OR e.blocked = true

        UNION ALL

        -- Get team rate limits and blocked status
        SELECT
            'team' as entity_type,
            team_id as entity_id,
            team_alias as entity_alias,
            tpm_limit,
            rpm_limit,
            max_parallel_requests,
            blocked as is_blocked
        FROM "LiteLLM_TeamTable"
        WHERE tpm_limit IS NOT NULL
           OR rpm_limit IS NOT NULL
           OR max_parallel_requests IS NOT NULL
           OR blocked = true
        """

    @staticmethod
    def get_budget_metrics() -> str:
        return """
        WITH budget_data AS (
            -- User budgets from EndUserTable
            SELECT
                b.budget_id,
                b.max_budget,
                b.soft_budget,
                b.budget_reset_at,
                e.user_id as entity_id,
                'user' as entity_type,
                u.user_alias as entity_alias,
                u.spend as current_spend
            FROM "LiteLLM_BudgetTable" b
            JOIN "LiteLLM_EndUserTable" e ON e.budget_id = b.budget_id
            LEFT JOIN "LiteLLM_UserTable" u ON u.user_id = e.user_id

            UNION ALL

            -- Team budgets from TeamMembership
            SELECT
                b.budget_id,
                b.max_budget,
                b.soft_budget,
                b.budget_reset_at,
                tm.team_id as entity_id,
                'team' as entity_type,
                t.team_alias as entity_alias,
                t.spend as current_spend
            FROM "LiteLLM_BudgetTable" b
            JOIN "LiteLLM_TeamMembership" tm ON tm.budget_id = b.budget_id
            LEFT JOIN "LiteLLM_TeamTable" t ON t.team_id = tm.team_id

            UNION ALL

            -- Organization budgets from OrganizationMembership
            SELECT
                b.budget_id,
                b.max_budget,
                b.soft_budget,
                b.budget_reset_at,
                om.organization_id as entity_id,
                'organization' as entity_type,
                o.organization_alias as entity_alias,
                o.spend as current_spend
            FROM "LiteLLM_BudgetTable" b
            JOIN "LiteLLM_OrganizationMembership" om ON om.budget_id = b.budget_id
            LEFT JOIN "LiteLLM_OrganizationTable" o ON o.organization_id = om.organization_id
        )
        SELECT * FROM budget_data
        """

    @staticmethod
    def get_key_metrics() -> str:
        return """
        SELECT
            token,
            key_name,
            key_alias,
            expires,
            user_id,
            team_id,
            blocked,
            spend
        FROM "LiteLLM_VerificationToken"
        """

    @staticmethod
    def get_key_spend() -> str:
        return """
        SELECT
            v.key_name,
            v.key_alias,
            SUM(l.spend) AS total_spend
        FROM "LiteLLM_SpendLogs" l
        LEFT JOIN "LiteLLM_VerificationToken" v ON l.api_key = v.token
        WHERE l."startTime" >= NOW() - INTERVAL '30 days'
        GROUP BY v.key_name, v.key_alias
        ORDER BY total_spend DESC
        """
